from unittest.mock import MagicMock,patch
from datetime import datetime
from backtester.data.sentiment_source import SentimentDataSource


def test_fetch_scores_headlines():
    fake_response = MagicMock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value= {
        "status" : "ok",
        "totalResults": 1,
        "articles" : [
            {
                "title": "Apple stock plunges after disastrous earnings",
                "publishedAt": "2026-07-20T12:00:00Z",
                "source": {"name": "Reuters"},
            }
        ]
    }

    with patch("backtester.data.sentiment_source.requests.get", return_value= fake_response):
        source = SentimentDataSource()
        df = source.fetch("AAPL", datetime(2026,7,1), datetime(2026,7,30))

        assert len(df)== 1
        assert df["headline"].iloc[0] == "Apple stock plunges after disastrous earnings"
        assert df["sentiment"].iloc[0] < 0
