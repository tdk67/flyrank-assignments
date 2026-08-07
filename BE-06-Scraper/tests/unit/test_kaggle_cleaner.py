from cleaner.kaggle_cleaner import (
    build_dataset_record,
    clean_tag_list,
    parse_metric_number,
)


def test_parse_metric_number():
    assert parse_metric_number("1.5k") == 1500
    assert parse_metric_number("2.3m") == 2300000
    assert parse_metric_number("500") == 500
    assert parse_metric_number(120) == 120
    assert parse_metric_number(None) == 0


def test_clean_tag_list():
    assert clean_tag_list("computer vision, AI &amp; ML, computer vision") == ["computer vision", "ai & ml"]
    assert clean_tag_list(["Python", " Machine Learning "]) == ["python", "machine learning"]
    assert clean_tag_list(None) == []


def test_build_dataset_record():
    record = build_dataset_record(
        dataset_url="/datasets/zsinghrahul/fake-news-detection",
        dataset_title="Fake News Detection &amp; Analysis",
        creator_username="zsinghrahul",
        upvotes_count="1.2k",
        views_count="15k",
        downloads_count="3000",
        license_name="CC0: Public Domain",
        summary_description="  A comprehensive dataset of fake and real news articles.  \n",
        tags="nlp, classification",
        last_updated_date="2026-06-15"
    )

    assert record.dataset_url == "https://www.kaggle.com/datasets/zsinghrahul/fake-news-detection"
    assert record.dataset_title == "Fake News Detection & Analysis"
    assert record.creator_username == "zsinghrahul"
    assert record.upvotes_count == 1200
    assert record.views_count == 15000
    assert record.downloads_count == 3000
    assert record.license_name == "CC0: Public Domain"
    assert record.summary_description == "A comprehensive dataset of fake and real news articles."
    assert record.tags == ["nlp", "classification"]
    assert record.last_updated_date == "2026-06-15"
