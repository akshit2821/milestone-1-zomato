from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/restaurants_raw.csv")
CLEAN_PATH = Path("data/restaurants_clean.csv")


def clean_frame(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "restaurant_name": "name",
        "location": "locality",
        "city_name": "city",
        "cost_for_two": "avg_cost_for_two",
    }
    df = df.rename(columns=rename_map)

    required = ["name", "city", "locality", "cuisines", "rating", "avg_cost_for_two"]
    for col in required:
        if col not in df.columns:
            df[col] = ""

    cleaned = df[required].copy()
    cleaned["name"] = cleaned["name"].astype(str).str.strip()
    cleaned["city"] = cleaned["city"].astype(str).str.strip().str.lower()
    cleaned["locality"] = cleaned["locality"].astype(str).str.strip().str.lower()
    cleaned["cuisines"] = cleaned["cuisines"].astype(str).str.strip().str.lower()
    cleaned["rating"] = pd.to_numeric(cleaned["rating"], errors="coerce").fillna(0.0)
    cleaned["avg_cost_for_two"] = pd.to_numeric(
        cleaned["avg_cost_for_two"], errors="coerce"
    ).fillna(0.0)

    cleaned = cleaned.dropna(subset=["name"])
    cleaned = cleaned.drop_duplicates(subset=["name", "city", "locality"], keep="first")
    return cleaned


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            "Expected raw input at data/restaurants_raw.csv. "
            "Place the raw dataset there and run this script again."
        )

    frame = pd.read_csv(RAW_PATH)
    cleaned = clean_frame(frame)
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEAN_PATH, index=False)
    print(f"Cleaned dataset written to {CLEAN_PATH} with {len(cleaned)} rows.")


if __name__ == "__main__":
    main()
