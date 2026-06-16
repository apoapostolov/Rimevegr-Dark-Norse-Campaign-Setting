from __future__ import annotations

import argparse
import base64
import hashlib
import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - import guard for scaffold state
    load_dotenv = None

try:
    import yaml
except ImportError:  # pragma: no cover - optional authoring dependency
    yaml = None

try:
    genai = importlib.import_module("google.genai")
except ImportError:  # pragma: no cover - import guard for scaffold state
    genai = None

KEY_NAMES = (
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "GEMINI_KEY",
)
DEFAULT_MODEL = "gemini-2.5-flash-image"
KNOWN_OPERATIONS = (
    "create",
    "preserve and restage",
    "transform",
    "edit only",
    "combine references into",
)
USD_TO_BGN_EST = 1.75
PRICING_REFERENCE_DATE = "2026-04-15"
SUPPORTED_IMAGE_MODELS: dict[str, dict[str, Any]] = {
    "gemini-2.5-flash-image": {
        "label": "Gemini 2.5 Flash Image",
        "family": "nanobanana",
        "method": "generate_content",
        "price_usd_per_image": 0.039,
        "pricing_note": "Published paid-tier price per image up to 1024x1024.",
    },
    "gemini-3.1-flash-image-preview": {
        "label": "Gemini 3.1 Flash Image Preview",
        "family": "nanobanana",
        "method": "generate_content",
        "price_usd_per_image": 0.067,
        "pricing_note": "Published paid-tier estimate for a 1K image.",
    },
    "gemini-3-pro-image-preview": {
        "label": "Nanobanana 2 Pro / Gemini 3 Pro Image Preview",
        "family": "nanobanana-pro",
        "method": "generate_content",
        "price_usd_per_image": 0.134,
        "pricing_note": "Published paid-tier estimate for a 1K or 2K image.",
    },
    "imagen-4.0-fast-generate-001": {
        "label": "Imagen 4 Fast",
        "family": "imagen",
        "method": "generate_images",
        "price_usd_per_image": 0.02,
        "pricing_note": "Published paid-tier image price.",
    },
    "imagen-4.0-generate-001": {
        "label": "Imagen 4 Standard",
        "family": "imagen",
        "method": "generate_images",
        "price_usd_per_image": 0.04,
        "pricing_note": "Published paid-tier image price.",
    },
    "imagen-4.0-ultra-generate-001": {
        "label": "Imagen 4 Ultra",
        "family": "imagen",
        "method": "generate_images",
        "price_usd_per_image": 0.06,
        "pricing_note": "Published paid-tier image price.",
    },
}
MODEL_ALIASES = {
    "nanobanana": "gemini-2.5-flash-image",
    "nano-banana": "gemini-2.5-flash-image",
    "nanobanana-2": "gemini-2.5-flash-image",
    "nanobanana-pro": "gemini-3-pro-image-preview",
    "nano-banana-pro": "gemini-3-pro-image-preview",
    "nanobanana 2 pro": "gemini-3-pro-image-preview",
    "nanobanana-2-pro": "gemini-3-pro-image-preview",
    "nano-banana 2 pro": "gemini-3-pro-image-preview",
    "gemini-3-pro": "gemini-3-pro-image-preview",
    "imagen-fast": "imagen-4.0-fast-generate-001",
    "imagen": "imagen-4.0-generate-001",
    "imagen-standard": "imagen-4.0-generate-001",
    "imagen-ultra": "imagen-4.0-ultra-generate-001",
}
DEFAULT_PROMPT_POLICY = {
    "selection_mode": "minimal_relevant",
    "include_scene_routing": "auto",
    "include_identity_lock": "auto",
    "include_change_request": "if_present",
    "include_continuity": "if_needed",
    "max_pressure_details": 3,
    "max_identity_traits": 3,
}
CHEAP_IMAGE_MODEL = "gemini-2.5-flash-image"
EXPENSIVE_IMAGE_MODEL = "gemini-3-pro-image-preview"
HIGH_END_MODEL_KEYWORDS = (
    "high-end",
    "high end",
    "hero image",
    "cover art",
    "key art",
    "premium",
    "precise",
    "precision",
    "high detail",
    "highly detailed",
    "intricate",
    "requirements",
    "exact requirements",
    "detailed illustration",
    "detailed portrait",
    "poster",
    "landmark hero",
)
CHEAP_MODEL_KEYWORDS = (
    "stock",
    "stock illustration",
    "chapter",
    "batch",
    "variants",
    "many images",
    "a lot of images",
    "filler",
    "simple illustration",
    "quick illustration",
    "exploration",
)
UPGRADE_SIGNAL_KEYWORDS = (
    "user dissatisfied",
    "dissatisfied",
    "not satisfied",
    "upgrade quality",
    "higher quality",
    "retry in pro",
)
NAMED_CHARACTER_PATTERNS: dict[str, str] = {
    "Voss Cold-Eye": r"\bvoss(?:\s+cold[- ]eye)?\b",
    "Gest Ledger": r"\bgest(?:\s+ledger)?\b",
    "Kell Hook": r"\bkell(?:\s+hook)?\b|\bthe door\b",
    "Thorne Ash-Born": r"\bthorne(?:\s+ash[- ]born)?\b",
    "Petra Shepherd": r"\bpetra(?:\s+shepherd)?\b",
    "Ash": r"\bash\b(?!\s+(?:tones?|mist|smoke|drift|wood|tree|grey|gray))",
    "Dalla": r"\bdalla\b",
    "Snorri": r"\bsnorri\b",
    "Ubbe Ironside": r"\bubbe(?:\s+ironside)?\b",
    "Orm": r"\borm\b",
    "Dagfinn": r"\bdagfinn\b",
    "Lump": r"\blump\b",
}


def load_repository_env(start_path: Path) -> Path | None:
    """Load the nearest repository .env without exposing secret values."""
    if load_dotenv is None:
        return None

    for candidate_dir in (start_path, *start_path.parents):
        env_path = candidate_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=False)
            return env_path

    return None


def resolve_api_key() -> tuple[str, str]:
    for key_name in KEY_NAMES:
        key_value = os.getenv(key_name)
        if key_value:
            return key_name, key_value

    raise RuntimeError(
        "No Gemini API key was found in the repository .env. "
        "Set one of: GEMINI_API_KEY, GOOGLE_API_KEY, or GEMINI_KEY."
    )


def load_prompt_batch(prompt_file: Path) -> dict[str, Any]:
    suffix = prompt_file.suffix.lower()
    with prompt_file.open("r", encoding="utf-8") as handle:
        if suffix in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError(
                    "PyYAML is not installed. Install requirements.txt before "
                    "using YAML prompt batches."
                )
            batch = yaml.safe_load(handle)
        else:
            batch = json.load(handle)

    if not isinstance(batch, dict):
        raise ValueError("Prompt batch root must be an object.")

    return batch


def _clean_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [value]

    if not isinstance(value, list):
        return []

    return [str(item).strip() for item in value if str(item).strip()]


def _validate_list_field(value: Any, label: str) -> None:
    if value is None:
        return

    if isinstance(value, (list, str)):
        return

    raise ValueError(f"{label} must be a list or string when provided.")


def _safe_int(value: Any, default: int) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return default


def _strip_literal_attractiveness_scale_language(text: str) -> str:
    cleaned = re.sub(
        r"\battractiveness\s+scale\s*[:=-]?\s*(-?\d+|very\s+low|low|plain|average|high)\b\s*:?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.;:])", r"\1", cleaned)
    return cleaned.strip()


def _collect_named_character_mentions(item: dict[str, Any]) -> list[str]:
    text_parts: list[str] = []
    for key in ("prompt", "notes", "change_request"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            text_parts.append(value.strip())

    structured_prompt = item.get("structured_prompt")
    if isinstance(structured_prompt, dict):
        for value in structured_prompt.values():
            if isinstance(value, str) and value.strip():
                text_parts.append(value.strip())

    identity_lock = item.get("identity_lock")
    if isinstance(identity_lock, dict):
        for key in ("identity_anchor",):
            value = identity_lock.get(key)
            if isinstance(value, str) and value.strip():
                text_parts.append(value.strip())
        refs = identity_lock.get("named_character_refs")
        text_parts.extend(_clean_list(refs))

    combined_text = " ".join(text_parts).lower()
    mentions: list[str] = []
    for canonical_name, pattern in NAMED_CHARACTER_PATTERNS.items():
        if re.search(pattern, combined_text, flags=re.IGNORECASE):
            mentions.append(canonical_name)

    return mentions


def _canonicalize_model_name(value: Any) -> str:
    raw_value = str(value or "").strip()
    if not raw_value:
        raw_value = DEFAULT_MODEL

    if raw_value.lower().startswith("models/"):
        raw_value = raw_value.split("/", 1)[1]

    return MODEL_ALIASES.get(raw_value.lower(), raw_value)


def _get_model_metadata(model_name: Any) -> dict[str, Any]:
    canonical_name = _canonicalize_model_name(model_name)
    metadata = SUPPORTED_IMAGE_MODELS.get(canonical_name, {}).copy()
    if not metadata:
        metadata = {
            "label": canonical_name,
            "family": "unknown",
            "method": (
                "generate_images" if canonical_name.startswith("imagen") else "generate_content"
            ),
            "price_usd_per_image": None,
            "pricing_note": "No built-in price estimate is stored for this model.",
        }

    metadata["name"] = canonical_name
    return metadata


def _resolve_number_of_images(
    override_count: Any, item: dict[str, Any], defaults: dict[str, Any]
) -> int:
    if override_count is not None:
        return max(1, _safe_int(override_count, 1))

    return max(1, _safe_int(item.get("number_of_images", defaults.get("number_of_images", 1)), 1))


def _normalize_model_preference(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    aliases = {
        "": "",
        "auto": "auto",
        "smart": "auto",
        "ai": "auto",
        "cheap": "cheap",
        "low": "cheap",
        "budget": "cheap",
        "stock": "cheap",
        "default": "cheap",
        "high": "expensive",
        "expensive": "expensive",
        "premium": "expensive",
        "pro": "expensive",
        "detailed": "expensive",
        "high-end": "expensive",
        "high end": "expensive",
    }
    return aliases.get(normalized, normalized)


def _is_auto_model_request(value: Any) -> bool:
    return _normalize_model_preference(value) == "auto"


def _estimate_batch_image_volume(batch: dict[str, Any], override_count: Any = None) -> tuple[int, int]:
    defaults = batch.get("defaults", {}) if isinstance(batch.get("defaults"), dict) else {}
    total_items = 0
    total_images = 0
    for item in batch.get("items", []):
        if not isinstance(item, dict):
            continue
        total_items += 1
        total_images += _resolve_number_of_images(override_count, item, defaults)
    return total_items, total_images


def _collect_model_selection_text(item: dict[str, Any], batch: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in (
        "prompt",
        "change_request",
        "notes",
        "model_preference",
        "quality_tier",
        "user_feedback",
    ):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())

    structured = item.get("structured_prompt")
    if isinstance(structured, dict):
        for value in structured.values():
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())

    routing = batch.get("scene_routing")
    if isinstance(routing, dict):
        for key in ("scene_family", "sub_scene", "subject_lens", "emotion"):
            value = routing.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())

    return " ".join(parts).lower()


def _prompt_for_uncertain_model_choice(item_id: str, reason: str) -> str:
    if not sys.stdin or not sys.stdin.isatty():
        raise RuntimeError(
            f"Automatic model choice is unclear for '{item_id}': {reason}. "
            f"Set an explicit model, set model_preference to cheap or high, or rerun with "
            f"--uncertain-model-behavior cheap or --uncertain-model-behavior expensive."
        )

    print(f"Model choice is unclear for item '{item_id}'. {reason}")
    print(
        f"Choose 'cheap' for {CHEAP_IMAGE_MODEL} or 'expensive' for {EXPENSIVE_IMAGE_MODEL}."
    )
    while True:
        answer = input("Confirm model choice [cheap/expensive]: ").strip().lower()
        if answer in {"cheap", "low", "budget", "c"}:
            return CHEAP_IMAGE_MODEL
        if answer in {"expensive", "high", "premium", "pro", "e", "h"}:
            return EXPENSIVE_IMAGE_MODEL
        print("Please answer 'cheap' or 'expensive'.")


def _select_model_for_item(
    item: dict[str, Any],
    batch: dict[str, Any],
    defaults: dict[str, Any],
    fallback_model: str,
    override_model: Any = None,
    uncertain_behavior: str = "ask",
    auto_choose_models: bool = False,
    total_items: int = 1,
    total_batch_images: int = 1,
) -> tuple[str, str]:
    if override_model:
        selected_model = _canonicalize_model_name(override_model)
        return selected_model, "CLI override forced a single model for the whole run."

    item_model = item.get("model")
    if isinstance(item_model, str) and item_model.strip() and not _is_auto_model_request(item_model):
        selected_model = _canonicalize_model_name(item_model)
        return selected_model, "Item-specific model override."

    explicit_preference = _normalize_model_preference(
        item.get("model_preference")
        or item.get("quality_tier")
        or defaults.get("model_preference")
        or batch.get("model_preference")
    )
    if explicit_preference == "cheap":
        return CHEAP_IMAGE_MODEL, "Explicit cheap or stock preference."
    if explicit_preference == "expensive":
        return EXPENSIVE_IMAGE_MODEL, "Explicit high-end or premium preference."

    if not auto_choose_models:
        selected_model = _canonicalize_model_name(fallback_model)
        return selected_model, "Batch or default model selection."

    item_id = str(item.get("id") or "unknown_item")
    number_of_images = _resolve_number_of_images(None, item, defaults)
    routing_text = _collect_model_selection_text(item, batch)

    has_high_end_signal = any(keyword in routing_text for keyword in HIGH_END_MODEL_KEYWORDS)
    has_cheap_signal = any(keyword in routing_text for keyword in CHEAP_MODEL_KEYWORDS)
    has_upgrade_signal = any(keyword in routing_text for keyword in UPGRADE_SIGNAL_KEYWORDS)
    high_volume_batch = total_batch_images > 6 or total_items > 4
    small_item_run = number_of_images <= 2

    if has_upgrade_signal:
        if small_item_run:
            return EXPENSIVE_IMAGE_MODEL, "User dissatisfaction or an upgrade request pushed this item to the premium model."
        reason = "The user wants higher quality, but the requested image count is large enough to make the premium route expensive."
        normalized_behavior = _normalize_model_preference(uncertain_behavior)
        if normalized_behavior == "cheap":
            return CHEAP_IMAGE_MODEL, f"Uncertain case defaulted to the cheaper model. {reason}"
        if normalized_behavior == "expensive":
            return EXPENSIVE_IMAGE_MODEL, f"Uncertain case defaulted to the premium model. {reason}"
        confirmed_model = _prompt_for_uncertain_model_choice(item_id, reason)
        return confirmed_model, f"User confirmed the model because the automatic choice was uncertain. {reason}"

    if has_high_end_signal:
        if small_item_run:
            return EXPENSIVE_IMAGE_MODEL, "High-detail or high-precision illustration in a small run."
        reason = "This prompt looks premium and detail-heavy, but the requested image count is too large for an automatic expensive recommendation."
        normalized_behavior = _normalize_model_preference(uncertain_behavior)
        if normalized_behavior == "cheap":
            return CHEAP_IMAGE_MODEL, f"Uncertain case defaulted to the cheaper model. {reason}"
        if normalized_behavior == "expensive":
            return EXPENSIVE_IMAGE_MODEL, f"Uncertain case defaulted to the premium model. {reason}"
        confirmed_model = _prompt_for_uncertain_model_choice(item_id, reason)
        return confirmed_model, f"User confirmed the model because the automatic choice was uncertain. {reason}"

    if has_cheap_signal:
        return CHEAP_IMAGE_MODEL, "Stock-style or batch-oriented wording favored the cheaper model."

    if high_volume_batch:
        return CHEAP_IMAGE_MODEL, "Large batch volume favored the cheaper model by default."

    reason = (
        "The prompt does not clearly read as either premium-detail limited output or stock-style batch output."
    )
    normalized_behavior = _normalize_model_preference(uncertain_behavior)
    if normalized_behavior == "cheap":
        return CHEAP_IMAGE_MODEL, f"Uncertain case defaulted to the cheaper model. {reason}"
    if normalized_behavior == "expensive":
        return EXPENSIVE_IMAGE_MODEL, f"Uncertain case defaulted to the premium model. {reason}"

    confirmed_model = _prompt_for_uncertain_model_choice(item_id, reason)
    return confirmed_model, f"User confirmed the model because the automatic choice was uncertain. {reason}"


def _format_price(cost_usd: float | None) -> str:
    if cost_usd is None:
        return "unknown"

    estimated_bgn = cost_usd * USD_TO_BGN_EST
    return f"${cost_usd:.3f} (~{estimated_bgn:.2f} BGN est.)"


def _estimate_cost_for_model(model_name: Any, image_count: int) -> tuple[float | None, str]:
    metadata = _get_model_metadata(model_name)
    price_usd_per_image = metadata.get("price_usd_per_image")
    if price_usd_per_image is None:
        return None, str(metadata.get("pricing_note", "Unknown price."))

    return float(price_usd_per_image) * image_count, str(metadata.get("pricing_note", ""))


def _collect_available_image_models(client: Any) -> set[str]:
    available_models: set[str] = set()
    for model in client.models.list():
        name = _canonicalize_model_name(getattr(model, "name", ""))
        if name in SUPPORTED_IMAGE_MODELS:
            available_models.add(name)

    return available_models


def _print_supported_models() -> None:
    print("Supported Gemini and Imagen image models:")
    for model_name, metadata in SUPPORTED_IMAGE_MODELS.items():
        price_text = _format_price(metadata.get("price_usd_per_image"))
        print(
            f" - {model_name}: {metadata.get('label')} | family={metadata.get('family')} | "
            f"estimated paid cost={price_text} | {metadata.get('pricing_note')}"
        )


def _resolve_prompt_policy(batch: dict[str, Any]) -> dict[str, Any]:
    raw_policy = batch.get("prompt_policy")
    if not isinstance(raw_policy, dict):
        raw_policy = {}

    return {
        "selection_mode": str(
            raw_policy.get(
                "selection_mode", DEFAULT_PROMPT_POLICY["selection_mode"]
            )
        )
        .strip()
        .lower(),
        "include_scene_routing": str(
            raw_policy.get(
                "include_scene_routing",
                DEFAULT_PROMPT_POLICY["include_scene_routing"],
            )
        )
        .strip()
        .lower(),
        "include_identity_lock": str(
            raw_policy.get(
                "include_identity_lock",
                DEFAULT_PROMPT_POLICY["include_identity_lock"],
            )
        )
        .strip()
        .lower(),
        "include_change_request": str(
            raw_policy.get(
                "include_change_request",
                DEFAULT_PROMPT_POLICY["include_change_request"],
            )
        )
        .strip()
        .lower(),
        "include_continuity": str(
            raw_policy.get(
                "include_continuity",
                DEFAULT_PROMPT_POLICY["include_continuity"],
            )
        )
        .strip()
        .lower(),
        "max_pressure_details": _safe_int(
            raw_policy.get(
                "max_pressure_details",
                DEFAULT_PROMPT_POLICY["max_pressure_details"],
            ),
            DEFAULT_PROMPT_POLICY["max_pressure_details"],
        ),
        "max_identity_traits": _safe_int(
            raw_policy.get(
                "max_identity_traits",
                DEFAULT_PROMPT_POLICY["max_identity_traits"],
            ),
            DEFAULT_PROMPT_POLICY["max_identity_traits"],
        ),
    }


def validate_prompt_batch(batch: dict[str, Any]) -> None:
    defaults = batch.get("defaults", {})
    if defaults and not isinstance(defaults, dict):
        raise ValueError("Prompt batch 'defaults' must be an object when provided.")

    scene_routing = batch.get("scene_routing")
    if scene_routing is not None and not isinstance(scene_routing, dict):
        raise ValueError("Prompt batch 'scene_routing' must be an object when provided.")

    prompt_policy = batch.get("prompt_policy")
    if prompt_policy is not None and not isinstance(prompt_policy, dict):
        raise ValueError("Prompt batch 'prompt_policy' must be an object when provided.")

    if "number_of_images" in defaults and _safe_int(defaults.get("number_of_images"), 0) <= 0:
        raise ValueError("Prompt batch 'defaults.number_of_images' must be >= 1.")

    _validate_list_field(defaults.get("reference_images"), "Defaults 'reference_images'")
    _validate_list_field(batch.get("reference_images"), "Batch-level 'reference_images'")

    items = batch.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("Prompt batch must include a non-empty 'items' list.")

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Prompt item {index} must be an object.")
        if not item.get("id"):
            raise ValueError(f"Prompt item {index} is missing an 'id'.")

        operation = item.get("operation") or defaults.get("operation")
        if operation is not None and not isinstance(operation, str):
            raise ValueError(f"Prompt item {index} has a non-string 'operation'.")

        if "model" in item and not isinstance(item.get("model"), str):
            raise ValueError(f"Prompt item {index} has a non-string 'model'.")

        if "number_of_images" in item and _safe_int(item.get("number_of_images"), 0) <= 0:
            raise ValueError(f"Prompt item {index} has an invalid 'number_of_images' value.")

        prompt_text = str(item.get("prompt") or "").strip()
        structured_prompt = item.get("structured_prompt")
        if structured_prompt is not None and not isinstance(structured_prompt, dict):
            raise ValueError(
                f"Prompt item {index} has a non-object 'structured_prompt' value."
            )
        if not prompt_text and not structured_prompt:
            raise ValueError(
                f"Prompt item {index} must include either 'prompt' or "
                f"'structured_prompt'."
            )

        _validate_list_field(
            item.get("reference_images"), f"Prompt item {index} 'reference_images'"
        )
        _validate_list_field(
            item.get("locked_elements"), f"Prompt item {index} 'locked_elements'"
        )
        _validate_list_field(
            item.get("continuity_notes"), f"Prompt item {index} 'continuity_notes'"
        )

        identity_lock = item.get("identity_lock")
        if identity_lock is not None:
            if not isinstance(identity_lock, dict):
                raise ValueError(
                    f"Prompt item {index} has a non-object 'identity_lock' value."
                )

            for field_name in (
                "immutable_traits",
                "flexible_traits",
                "allowed_scene_changes",
                "forbidden_drift",
                "reference_images",
                "continuity_notes",
                "named_character_refs",
            ):
                _validate_list_field(
                    identity_lock.get(field_name),
                    f"Prompt item {index} identity_lock '{field_name}'",
                )

        named_character_mentions = _collect_named_character_mentions(item)
        if named_character_mentions:
            if not isinstance(identity_lock, dict):
                raise ValueError(
                    f"Prompt item {index} references named character(s) "
                    f"{', '.join(named_character_mentions)} but is missing an identity_lock block."
                )

            identity_anchor = str(identity_lock.get("identity_anchor") or "").strip()
            attractiveness_scale = str(identity_lock.get("attractiveness_scale") or "").strip()
            immutable_traits = _clean_list(identity_lock.get("immutable_traits"))
            forbidden_drift = _clean_list(identity_lock.get("forbidden_drift"))

            if not identity_anchor:
                raise ValueError(
                    f"Prompt item {index} references named character(s) "
                    f"{', '.join(named_character_mentions)} but is missing identity_lock.identity_anchor."
                )
            if not attractiveness_scale:
                raise ValueError(
                    f"Prompt item {index} references named character(s) "
                    f"{', '.join(named_character_mentions)} but is missing identity_lock.attractiveness_scale."
                )
            if not immutable_traits and not forbidden_drift:
                raise ValueError(
                    f"Prompt item {index} references named character(s) "
                    f"{', '.join(named_character_mentions)} but does not include stable canon guidance in immutable_traits or forbidden_drift."
                )


def _ensure_operation_prefix(text: str, operation: str) -> str:
    lowered = text.lower().strip()
    if any(lowered.startswith(f"{known} ") for known in KNOWN_OPERATIONS):
        return text.strip()

    return f"{operation.capitalize()} {text.strip()}"


def _build_structured_sentence(structured: dict[str, Any], operation: str) -> str:
    subject = str(structured.get("subject") or "the requested subject").strip()
    action = str(structured.get("action") or "").strip()
    setting = str(structured.get("setting") or "").strip()
    mood = str(structured.get("mood") or "").strip()
    camera = str(structured.get("camera") or "").strip()

    sentence = f"{operation.capitalize()} {subject}"
    if action:
        sentence += f", {action}"
    if setting:
        sentence += f", in {setting}"
    if mood:
        sentence += f", with {mood}"
    if camera:
        sentence += f", {camera}"

    return sentence


def _build_scene_routing_summary(
    batch: dict[str, Any], policy: dict[str, Any], base_text: str
) -> str:
    routing = batch.get("scene_routing")
    if not isinstance(routing, dict):
        return ""

    mode = str(policy.get("include_scene_routing", "auto")).lower()
    if mode in {"off", "never", "false"}:
        return ""

    text_lower = base_text.lower()
    parts: list[str] = []

    scene_focus = str(routing.get("sub_scene") or "").strip()
    scene_family = str(routing.get("scene_family") or "").strip()
    subject_lens = str(routing.get("subject_lens") or "").strip()
    emotion = str(routing.get("emotion") or "").strip()
    color_family = str(routing.get("color_family") or "").strip()

    if mode in {"always", "full", "true"}:
        if scene_family:
            parts.append(f"scene family: {scene_family}")
        if scene_focus:
            parts.append(f"sub scene: {scene_focus}")
        if subject_lens:
            parts.append(f"subject lens: {subject_lens}")
    else:
        if scene_focus and scene_focus.lower() not in text_lower:
            parts.append(f"scene focus: {scene_focus}")
        elif scene_family and scene_family.lower() not in text_lower:
            parts.append(f"scene family: {scene_family}")

    if emotion and emotion.lower() not in text_lower:
        parts.append(f"emotion: {emotion}")
    if color_family and color_family.lower() not in text_lower:
        parts.append(f"color family: {color_family}")

    pressure_cues: list[str] = []
    max_pressure_details = int(policy.get("max_pressure_details", 3))
    for key in (
        "material_pressure",
        "social_pressure",
        "environmental_pressure",
        "violence_pressure",
    ):
        for value in _clean_list(routing.get(key)):
            lowered = value.lower()
            if lowered in text_lower or value in pressure_cues:
                continue
            pressure_cues.append(value)
            if len(pressure_cues) >= max_pressure_details:
                break
        if len(pressure_cues) >= max_pressure_details:
            break

    if pressure_cues:
        parts.append(f"pressure cues: {'; '.join(pressure_cues)}")

    optional_overlays: list[str] = []
    for key in ("veil_level", "hush_type", "cracking"):
        value = str(routing.get(key) or "").strip()
        if value and value.lower() != "none":
            label = key.replace("_", " ")
            optional_overlays.append(f"{label}: {value}")

    if optional_overlays:
        parts.append(f"optional overlays: {'; '.join(optional_overlays)}")

    if not parts:
        return ""

    return f"Routing context: {' | '.join(parts)}."


def _describe_attractiveness_scale(value: str) -> str:
    normalized = str(value).strip().lower()
    mapping = {
        "-2": "Overall character read should feel feral, hunted, gaunt, and socially stripped; harsh face, defensive or predatory stance, and degraded improvised clothing with no residual glamour.",
        "-1": "Overall character read should stay distinctly unattractive and depleted; coarse features, tired posture, and badly worn clothing.",
        "0": "Overall character read should stay plain, severe, and unflattering; practical stance and utilitarian clothing with little beauty emphasis.",
        "1": "Overall character read should stay harsh, scarred, and unbeautified; disciplined stance and weather-worn practical kit.",
        "2": "Overall character read should stay rough, weathered, asymmetrical, and plainly human; grounded posture and worn but serviceable clothing.",
        "3": "Overall character read should stay capable, lived-in, and somewhat striking without glamour; confident posture and maintained practical clothing.",
        "4": "The person may read as notable-looking, but still scarred, tired, disciplined, and materially grounded rather than polished.",
        "5": "Use exceptional beauty only if explicitly intended, while keeping posture, clothing, and material reality historical rather than glossy.",
        "very low": "Overall character read should feel feral, hunted, gaunt, and socially stripped; harsh face, defensive or predatory stance, and degraded improvised clothing with no residual glamour.",
        "low": "Overall character read should stay distinctly unattractive and depleted; coarse features, tired posture, and badly worn clothing.",
        "plain": "Overall character read should stay plain, severe, and unflattering; practical stance and utilitarian clothing with little beauty emphasis.",
        "average": "Overall character read should stay capable, lived-in, and human without glamorization.",
        "high": "The person may read as notable-looking, but still scarred, tired, disciplined, and materially grounded rather than polished.",
    }
    return mapping.get(normalized, "")


def build_compiled_prompt(item: dict[str, Any], batch: dict[str, Any]) -> str:
    defaults = batch.get("defaults", {}) if isinstance(batch.get("defaults"), dict) else {}
    policy = _resolve_prompt_policy(batch)
    operation = str(item.get("operation") or defaults.get("operation") or "create").strip()
    prompt_text = _strip_literal_attractiveness_scale_language(
        str(item.get("prompt") or "").strip()
    )
    structured = item.get("structured_prompt")
    if not isinstance(structured, dict):
        structured = {}

    identity = item.get("identity_lock")
    if not isinstance(identity, dict):
        identity = {}

    segments: list[str] = []
    if prompt_text:
        base_text = _ensure_operation_prefix(prompt_text, operation)
    elif structured:
        base_text = _build_structured_sentence(structured, operation)
    else:
        base_text = f"{operation.capitalize()} the requested Rimevegr scene."
    segments.append(base_text)

    routing_summary = _build_scene_routing_summary(batch, policy, base_text)
    if routing_summary:
        segments.append(routing_summary)

    is_continuity_operation = operation.lower() in {
        "preserve and restage",
        "transform",
        "edit only",
        "combine references into",
    }
    include_identity_lock = str(policy.get("include_identity_lock", "auto")).lower()
    include_change_request = str(policy.get("include_change_request", "if_present")).lower()
    include_continuity = str(policy.get("include_continuity", "if_needed")).lower()
    max_identity_traits = int(policy.get("max_identity_traits", 3))

    identity_anchor = str(identity.get("identity_anchor") or "").strip()
    attractiveness_scale = str(identity.get("attractiveness_scale") or "").strip()
    immutable = _clean_list(identity.get("immutable_traits"))[:max_identity_traits]
    flexible = _clean_list(identity.get("flexible_traits"))[:max_identity_traits]
    allowed = _clean_list(identity.get("allowed_scene_changes"))[:max_identity_traits]
    forbidden = _clean_list(identity.get("forbidden_drift"))[:max_identity_traits]
    weathering_cues = _clean_list(identity.get("weathering_cues"))[:max_identity_traits]
    continuity = _clean_list(identity.get("continuity_notes"))[:max_identity_traits]
    locked_elements = _clean_list(item.get("locked_elements"))[:max_identity_traits]
    item_continuity = _clean_list(item.get("continuity_notes"))[:max_identity_traits]
    change_request = str(item.get("change_request") or "").strip()

    should_include_identity = False
    if identity:
        if include_identity_lock in {"always", "full", "true"}:
            should_include_identity = True
        elif include_identity_lock not in {"off", "never", "false"}:
            should_include_identity = is_continuity_operation or bool(identity_anchor)

    if should_include_identity:
        if identity_anchor:
            cleaned_identity_anchor = identity_anchor.rstrip(". ")
            segments.append(f"This should read as {cleaned_identity_anchor}.")
        scale_text = _describe_attractiveness_scale(attractiveness_scale)
        if scale_text:
            segments.append(scale_text)
        if immutable:
            segments.append(f"Keep fixed: {'; '.join(immutable)}.")
        if weathering_cues:
            segments.append(f"Weathering cues: {'; '.join(weathering_cues)}.")
        if is_continuity_operation and flexible:
            segments.append(f"Allow variation in: {'; '.join(flexible)}.")
        if is_continuity_operation and allowed:
            segments.append(f"Allowed scene changes: {'; '.join(allowed)}.")
        if forbidden:
            segments.append(f"Avoid: {'; '.join(forbidden)}.")

    if locked_elements:
        segments.append(f"Locked elements: {'; '.join(locked_elements)}.")

    if change_request and include_change_request not in {"off", "never", "false"}:
        segments.append(f"Requested change: {change_request}.")

    if continuity or item_continuity:
        notes = continuity + item_continuity
        if include_continuity in {"always", "full", "true"}:
            segments.append(f"Continuity notes: {'; '.join(notes)}.")
        elif include_continuity not in {"off", "never", "false"} and is_continuity_operation:
            segments.append(f"Continuity notes: {'; '.join(notes)}.")

    return " ".join(segment.strip() for segment in segments if segment.strip())


def resolve_reference_images(
    cli_paths: list[str], batch: dict[str, Any], prompt_file: Path
) -> list[Path]:
    candidates: list[str] = []

    defaults = batch.get("defaults", {})
    if isinstance(defaults, dict):
        candidates.extend(_clean_list(defaults.get("reference_images")))

    candidates.extend(_clean_list(batch.get("reference_images")))

    items = batch.get("items", [])
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue

            candidates.extend(_clean_list(item.get("reference_images")))

            identity_lock = item.get("identity_lock")
            if isinstance(identity_lock, dict):
                candidates.extend(_clean_list(identity_lock.get("reference_images")))

    candidates.extend(_clean_list(cli_paths))

    resolved: list[Path] = []
    seen: set[str] = set()
    for raw_path in candidates:
        path = Path(raw_path)
        if path.is_absolute():
            candidate_paths = [path.resolve()]
        else:
            candidate_paths = [
                (Path.cwd() / path).resolve(),
                (prompt_file.parent / path).resolve(),
                (prompt_file.parent.parent / path).resolve(),
            ]

        existing_path = next(
            (candidate for candidate in candidate_paths if candidate.exists()), None
        )
        if existing_path is None:
            tried = ", ".join(str(candidate) for candidate in candidate_paths)
            raise FileNotFoundError(
                f"Concept reference file not found for '{raw_path}'. Tried: {tried}"
            )

        key = str(existing_path).lower()
        if key in seen:
            continue

        seen.add(key)
        resolved.append(existing_path)

    return resolved


def build_client(api_key: str):
    if genai is None:
        raise RuntimeError(
            "google-genai is not installed. Install requirements.txt before live use."
        )

    return genai.Client(api_key=api_key)


def _safe_name(value: str) -> str:
    cleaned = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_" for char in value
    ).strip("_")
    return cleaned or "generated_image"


def _mime_extension(mime_type: str) -> str:
    mime_lower = str(mime_type or "").lower()
    if "png" in mime_lower:
        return ".png"
    if "jpeg" in mime_lower or "jpg" in mime_lower:
        return ".jpg"
    if "webp" in mime_lower:
        return ".webp"
    return ".bin"


def _write_inline_image_data(data: Any, output_path: Path) -> None:
    if isinstance(data, bytes):
        output_path.write_bytes(data)
        return

    if isinstance(data, str):
        output_path.write_bytes(base64.b64decode(data))
        return

    raise RuntimeError("Unsupported inline image payload type returned by API.")


def _extract_saved_images(response: Any, output_dir: Path, file_stem: str) -> list[Path]:
    saved_paths: list[Path] = []
    seen_hashes: set[str] = set()

    generated_images = getattr(response, "generated_images", None)
    if generated_images:
        for index, generated_image in enumerate(generated_images, start=1):
            image_obj = getattr(generated_image, "image", None)
            if image_obj is None:
                continue

            output_path = output_dir / f"{file_stem}_{index}.png"
            image_obj.save(output_path)
            digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
            if digest in seen_hashes:
                output_path.unlink(missing_ok=True)
                continue
            seen_hashes.add(digest)
            saved_paths.append(output_path)

    parts: list[Any] = []
    response_parts = getattr(response, "parts", None)
    if response_parts:
        parts.extend(response_parts)

    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        candidate_parts = getattr(content, "parts", None)
        if candidate_parts:
            parts.extend(candidate_parts)

    inline_index = len(saved_paths)
    for part in parts:
        inline_data = getattr(part, "inline_data", None)
        if inline_data is None:
            continue

        raw_data = getattr(inline_data, "data", b"")
        if isinstance(raw_data, str):
            raw_bytes = base64.b64decode(raw_data)
        elif isinstance(raw_data, bytes):
            raw_bytes = raw_data
        else:
            continue

        digest = hashlib.sha256(raw_bytes).hexdigest()
        if digest in seen_hashes:
            continue

        seen_hashes.add(digest)
        inline_index += 1
        mime_type = getattr(inline_data, "mime_type", "image/png")
        extension = _mime_extension(mime_type)
        output_path = output_dir / f"{file_stem}_{inline_index}{extension}"
        output_path.write_bytes(raw_bytes)
        saved_paths.append(output_path)

    return saved_paths


def _execute_item_generation(
    client: Any,
    model_name: str,
    compiled_prompt: str,
    aspect_ratio: str,
    output_dir: Path,
    file_stem: str,
    number_of_images: int,
) -> list[Path]:
    metadata = _get_model_metadata(model_name)
    resolved_model_name = str(metadata["name"])

    if genai is None:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install google-genai"
        )

    if metadata.get("method") == "generate_images":
        response = client.models.generate_images(
            model=resolved_model_name,
            prompt=compiled_prompt,
            config=genai.types.GenerateImagesConfig(
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio,
                output_mime_type="image/png",
            ),
        )
        return _extract_saved_images(response, output_dir, file_stem)

    saved_paths: list[Path] = []
    for image_index in range(1, number_of_images + 1):
        response = client.models.generate_content(
            model=resolved_model_name,
            contents=compiled_prompt,
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=genai.types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                ),
            ),
        )
        suffix = file_stem if number_of_images == 1 else f"{file_stem}_{image_index}"
        saved_paths.extend(_extract_saved_images(response, output_dir, suffix))

    return saved_paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Rimevegr prompt batches, inspect model access, and run image generation."
    )
    parser.add_argument(
        "--prompt-file",
        help=(
            "Path to a JSON or YAML prompt batch file. Required unless you are using "
            "only --list-supported-models or --check-available-models."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "images"),
        help="Directory reserved for final generated images.",
    )
    parser.add_argument(
        "--concept-image",
        action="append",
        default=[],
        help=(
            "Optional concept or reference image path for preserving character sameness. "
            "Pass more than once to include multiple references."
        ),
    )
    parser.add_argument(
        "--model",
        help=(
            "Exact Gemini or Imagen image model to use for the whole run, such as "
            "gemini-2.5-flash-image or imagen-4.0-fast-generate-001."
        ),
    )
    parser.add_argument(
        "--auto-choose-models",
        action="store_true",
        help=(
            "Let the script route each prompt item to the cheap or premium model "
            "automatically based on detail level, precision, and batch size."
        ),
    )
    parser.add_argument(
        "--uncertain-model-behavior",
        choices=["ask", "cheap", "expensive"],
        default="ask",
        help=(
            "What to do when automatic model routing is unclear: ask for confirmation, "
            "or force the cheap or expensive choice."
        ),
    )
    parser.add_argument(
        "--number-of-images",
        type=int,
        help="Override the number of images to create for each prompt item.",
    )
    parser.add_argument(
        "--list-supported-models",
        action="store_true",
        help="List all supported Gemini and Imagen family image models with cost estimates.",
    )
    parser.add_argument(
        "--check-available-models",
        action="store_true",
        help="Check which supported image models are currently available on the active API key without generating images.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Perform live generation. Without this flag the script stays in dry-run mode.",
    )
    args = parser.parse_args()

    if args.number_of_images is not None and args.number_of_images < 1:
        parser.error("--number-of-images must be at least 1.")

    if not args.prompt_file and not args.list_supported_models and not args.check_available_models:
        parser.error(
            "Provide --prompt-file, or use --list-supported-models and or --check-available-models."
        )

    if args.list_supported_models:
        _print_supported_models()
        print(f"Pricing reference date: {PRICING_REFERENCE_DATE}")
        print("Free-tier note: if your usage stays inside the Google AI Studio free quota, billed cost may still be $0.")
        if not args.prompt_file and not args.check_available_models:
            return 0

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    start_path = Path(args.prompt_file).resolve().parent if args.prompt_file else Path.cwd()
    env_path = load_repository_env(start_path)
    key_name, api_key = resolve_api_key()
    client = build_client(api_key)
    available_models = _collect_available_image_models(client)

    print(
        f"Supported image models available on this API key: {len(available_models)}/{len(SUPPORTED_IMAGE_MODELS)}"
    )
    for supported_model in sorted(SUPPORTED_IMAGE_MODELS):
        status = "available" if supported_model in available_models else "not available"
        print(f" - {supported_model}: {status}")

    if args.check_available_models and not args.prompt_file:
        return 0

    prompt_file = Path(args.prompt_file).resolve()
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    batch = load_prompt_batch(prompt_file)
    validate_prompt_batch(batch)
    reference_images = resolve_reference_images(args.concept_image, batch, prompt_file)

    defaults = batch.get("defaults", {}) if isinstance(batch.get("defaults"), dict) else {}
    batch_model_value = batch.get("model") or os.getenv("RIMEVEGR_IMAGE_MODEL", DEFAULT_MODEL)
    auto_choose_models = bool(
        args.auto_choose_models
        or _is_auto_model_request(batch_model_value)
        or _is_auto_model_request(defaults.get("model_preference"))
        or _is_auto_model_request(batch.get("model_preference"))
    )
    fallback_model = _canonicalize_model_name(
        batch_model_value if not _is_auto_model_request(batch_model_value) else DEFAULT_MODEL
    )
    model_name = (
        "auto per-item routing" if auto_choose_models and not args.model else _canonicalize_model_name(args.model or fallback_model)
    )
    if args.model and _canonicalize_model_name(args.model) not in available_models:
        raise RuntimeError(
            f"Requested model is not available on the current API key: {_canonicalize_model_name(args.model)}"
        )
    if not auto_choose_models and not args.model and fallback_model not in available_models:
        raise RuntimeError(
            f"Requested model is not available on the current API key: {fallback_model}"
        )

    batch_total_items, batch_total_images = _estimate_batch_image_volume(batch, args.number_of_images)

    item_runs: list[dict[str, Any]] = []
    total_requested_images = 0
    total_estimated_cost_usd = 0.0
    has_unknown_cost = False

    for index, item in enumerate(batch["items"], start=1):
        if not isinstance(item, dict):
            continue

        item_id = str(item.get("id", f"item_{index}"))
        item_model, model_reason = _select_model_for_item(
            item=item,
            batch=batch,
            defaults=defaults,
            fallback_model=fallback_model,
            override_model=args.model,
            uncertain_behavior=args.uncertain_model_behavior,
            auto_choose_models=auto_choose_models,
            total_items=batch_total_items,
            total_batch_images=batch_total_images,
        )
        if item_model not in available_models:
            raise RuntimeError(
                f"Prompt item '{item_id}' requests a model that is not available on this API key: {item_model}"
            )

        item_aspect_ratio = str(
            item.get("aspect_ratio") or defaults.get("aspect_ratio") or "16:9"
        ).strip()
        number_of_images = _resolve_number_of_images(args.number_of_images, item, defaults)
        compiled_prompt = build_compiled_prompt(item, batch)
        estimated_cost_usd, pricing_note = _estimate_cost_for_model(item_model, number_of_images)
        estimated_cost_text = _format_price(estimated_cost_usd)

        total_requested_images += number_of_images
        if estimated_cost_usd is None:
            has_unknown_cost = True
        else:
            total_estimated_cost_usd += estimated_cost_usd

        item_runs.append(
            {
                "item_id": item_id,
                "model_name": item_model,
                "aspect_ratio": item_aspect_ratio,
                "number_of_images": number_of_images,
                "compiled_prompt": compiled_prompt,
                "estimated_cost_usd": estimated_cost_usd,
                "estimated_cost_text": estimated_cost_text,
                "pricing_note": pricing_note,
                "model_reason": model_reason,
            }
        )

    print(f"Loaded batch: {batch.get('batch_name', 'unnamed-batch')}")
    print(f"Prompt items: {len(item_runs)}")
    print(f"Images requested in this run: {total_requested_images}")
    print(f"Prompt format: {prompt_file.suffix.lower() or '.json'}")
    print(f"Configured model target: {model_name}")
    print(f"Automatic per-item routing: {'enabled' if auto_choose_models and not args.model else 'disabled'}")
    print(f"Gemini key source: {key_name}")
    if env_path is not None:
        print(f"Environment file loaded: {env_path}")
    print(f"Output directory ready: {output_dir}")
    print(f"Pricing reference date: {PRICING_REFERENCE_DATE}")
    if reference_images:
        print(f"Concept reference images: {len(reference_images)}")
        for reference_path in reference_images:
            print(f" - {reference_path}")
    else:
        print("Concept reference images: none supplied")

    print("Estimated paid-tier cost by item:")
    for item_run in item_runs:
        print(
            f" - {item_run['item_id']}: {item_run['model_name']} x{item_run['number_of_images']} -> "
            f"{item_run['estimated_cost_text']} | {item_run['model_reason']}"
        )

    if has_unknown_cost:
        print("Total estimated paid-tier cost: partially unknown because at least one model has no built-in pricing metadata.")
    else:
        print(f"Total estimated paid-tier cost for this run: {_format_price(total_estimated_cost_usd)}")
    print("Free-tier note: if your usage stays inside the Google AI Studio free quota, billed cost may still be $0.")

    print("Compiled prompt previews:")
    for item_run in item_runs:
        preview = " ".join(item_run["compiled_prompt"].split())
        if len(preview) > 260:
            preview = f"{preview[:257]}..."
        print(
            f" - {item_run['item_id']} [{item_run['model_name']} x{item_run['number_of_images']} | {item_run['estimated_cost_text']}]: {preview}"
        )

    if not args.execute:
        print("Dry run only. No API calls were made.")
        return 0

    batch_name = _safe_name(str(batch.get("batch_name", "unnamed_batch")))
    saved_paths: list[Path] = []

    print("Live execution approved. Generating images now...")
    for item_run in item_runs:
        item_id_safe = _safe_name(item_run["item_id"])
        file_stem = f"{batch_name}_{item_id_safe}"

        print(
            f"Generating {item_run['item_id']} with model {item_run['model_name']} "
            f"at aspect ratio {item_run['aspect_ratio']} x{item_run['number_of_images']}..."
        )
        item_saved_paths = _execute_item_generation(
            client=client,
            model_name=item_run["model_name"],
            compiled_prompt=item_run["compiled_prompt"],
            aspect_ratio=item_run["aspect_ratio"],
            output_dir=output_dir,
            file_stem=file_stem,
            number_of_images=item_run["number_of_images"],
        )
        if not item_saved_paths:
            raise RuntimeError(
                f"The API returned no image data for item '{item_run['item_id']}'."
            )

        saved_paths.extend(item_saved_paths)

    print(f"Generated image files: {len(saved_paths)}")
    for saved_path in saved_paths:
        print(f" - {saved_path}")

    if has_unknown_cost:
        print("Total estimated paid-tier cost for generated output: partially unknown.")
    else:
        print(f"Total estimated paid-tier cost for generated output: {_format_price(total_estimated_cost_usd)}")
    print("Free-tier note: if your usage stays inside the Google AI Studio free quota, billed cost may still be $0.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
