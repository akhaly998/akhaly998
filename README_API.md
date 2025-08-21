# Name Similarity Checker API

This FastAPI application checks the similarity between a given name and names in a blacklist using advanced string similarity algorithms. It's designed to work with Arabic names and provides multiple similarity scoring methods.

## 🚀 Features

- **Multi-algorithm Similarity Checking**: Uses ratio, partial ratio, token sort ratio, and token set ratio
- **Arabic Text Support**: Optimized for Arabic names and text
- **Configurable Threshold**: Set custom similarity thresholds for matching
- **RESTful API**: Easy-to-use HTTP endpoints
- **CSV-based Blacklist**: Simple file-based storage for blacklisted names
- **Detailed Results**: Get comprehensive similarity scores and category information

## 📋 Requirements

- Python 3.7+
- FastAPI
- uvicorn
- pandas
- fuzzywuzzy
- python-levenshtein

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Endpoints

#### 1. `GET /` - Root Information
Returns basic API information and available endpoints.

#### 2. `POST /check-name` - Check Name Similarity
Check if a name matches any entry in the blacklist above a specified threshold.

**Request Body:**
```json
{
    "name": "صدام حسن سعيد مجيد",
    "threshold": 60.0
}
```

**Response:**
```json
{
    "input_name": "صدام حسن سعيد مجيد",
    "is_match": true,
    "matches": [
        {
            "blacklist_name": "صدام حسين",
            "similarity_score": 89.0,
            "category": "political_figure",
            "notes": "Former Iraqi President"
        }
    ],
    "highest_similarity": 89.0
}
```

#### 3. `GET /similarity/{name}` - Get Detailed Similarity Scores
Get detailed similarity scores for a name against all blacklisted entries.

**Example:** `GET /similarity/صدام حسن سعيد مجيد`

**Response:**
```json
{
    "input_name": "صدام حسن سعيد مجيد",
    "results": [
        {
            "blacklist_name": "صدام حسين",
            "category": "political_figure",
            "similarity_scores": {
                "ratio": 59,
                "partial_ratio": 89,
                "token_sort_ratio": 59,
                "token_set_ratio": 62,
                "max_score": 89
            }
        }
    ]
}
```

#### 4. `GET /blacklist` - View Blacklist
Get all entries in the blacklist.

#### 5. `POST /add-to-blacklist` - Add New Entry
Add a new name to the blacklist.

**Parameters:**
- `name`: The name to add
- `category`: Category (e.g., "terrorist", "criminal", "political_figure")
- `notes`: Additional notes about the person

## 🧪 Testing

### Using the Test Script
```bash
python test_api.py
```

### Using curl
```bash
# Test name checking
curl -X POST "http://localhost:8000/check-name" \
  -H "Content-Type: application/json" \
  -d '{"name": "صدام حسن سعيد مجيد", "threshold": 60.0}'

# Get similarity scores
curl -X GET "http://localhost:8000/similarity/صدام%20حسن%20سعيد%20مجيد"

# View blacklist
curl -X GET "http://localhost:8000/blacklist"
```

### Interactive API Documentation
Visit `http://localhost:8000/docs` for Swagger UI documentation.

## 📊 Similarity Algorithms

The application uses four different similarity algorithms from the fuzzywuzzy library:

1. **Ratio**: Basic Levenshtein distance ratio
2. **Partial Ratio**: Best partial string matching
3. **Token Sort Ratio**: Compares sorted tokens
4. **Token Set Ratio**: Compares token sets

The maximum score from all algorithms is used as the final similarity score.

## 📁 File Structure

```
.
├── main.py              # FastAPI application
├── blacklist.csv        # Blacklist data
├── requirements.txt     # Python dependencies
├── test_api.py         # Test script
└── README_API.md       # This documentation
```

## 🗂️ Blacklist Format

The `blacklist.csv` file contains the following columns:
- `name`: The blacklisted name (Arabic or any language)
- `category`: Category (terrorist, criminal, political_figure, suspicious)
- `notes`: Additional information about the person

## 🔧 Configuration

### Similarity Threshold
The default threshold is 80%, but you can adjust it in API calls:
- Lower threshold (e.g., 60%): More sensitive, catches more potential matches
- Higher threshold (e.g., 90%): More strict, only very close matches

### Adding New Names
You can add names via:
1. Direct API call to `/add-to-blacklist`
2. Editing the `blacklist.csv` file directly

## 🌍 Arabic Text Support

The application is optimized for Arabic text and handles:
- Right-to-left text direction
- Arabic character variations
- Word order differences
- Partial name matching

## 📖 Example Usage

```python
import requests

# Check a name
response = requests.post("http://localhost:8000/check-name", 
                        json={"name": "صدام حسن سعيد مجيد", "threshold": 70.0})
result = response.json()

if result['is_match']:
    print(f"⚠️  Warning: Name matches blacklist!")
    for match in result['matches']:
        print(f"Match: {match['blacklist_name']} ({match['similarity_score']}%)")
else:
    print("✅ Name not found in blacklist")
```

## 🔍 Test Results

The system successfully identifies the provided name "صدام حسن سعيد مجيد" as similar to "صدام حسين" in the blacklist with an 89% similarity score, demonstrating effective Arabic name matching capabilities.