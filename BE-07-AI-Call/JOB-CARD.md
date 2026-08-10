# Job Card: Book Record Translation API

## What it does (one sentence)
Translates a scraped book record's title and description into a target language (German, French, Italian, or English) returning clean, validated JSON.

## Input
```json
{
  "book_id": "string (valid ID from books.jsonl)",
  "target_language": "one of [de|fr|it|en]"
}
```

## Output
```json
{
  "book_id": "string",
  "target_language": "one of [de|fr|it|en]",
  "translated_title": "string",
  "translated_description": "string",
  "confidence": 0.95
}
```

## It must never
- Invent target languages outside the allowed enum `[de, fr, it, en]`.
- Return raw free text or markdown code fences (` ```json ` wrapper).
- Call the LLM model if `book_id` is missing from the database or if `target_language` is unsupported.
- Alter numerical facts, prices, or structural book metadata.
- Expose raw prompt text or internal error tracebacks.

## When unsure it should
- Set `confidence` below 0.5 and perform a literal translation without hallucinating missing details.
