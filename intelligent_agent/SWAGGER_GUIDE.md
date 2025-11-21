# Swagger/OpenAPI Documentation Guide

## What is BaseModel?

`BaseModel` is from **Pydantic** - a Python library for data validation. In FastAPI, it's used to:

### 1. **Define Request/Response Schemas**
```python
class QueryRequest(BaseModel):
    text: str
    thread_id: Optional[str] = None
    max_results: Optional[int] = 5
```

### 2. **Automatic Validation**
- Validates incoming data types
- Rejects invalid data automatically
- Returns clear error messages

### 3. **Auto-generates Swagger/OpenAPI Docs**
- FastAPI reads your BaseModel classes
- Automatically creates API documentation
- Shows request/response schemas

### 4. **Type Safety**
- Ensures data matches expected types
- Prevents runtime errors
- Better IDE support

## Benefits of BaseModel

### ✅ **Automatic Validation**
```python
# If user sends wrong type:
{"text": 123}  # ❌ Error: text must be string
{"text": "query"}  # ✅ Valid
```

### ✅ **Auto Documentation**
- Swagger UI shows all fields
- Shows types, defaults, examples
- Interactive testing

### ✅ **Data Conversion**
```python
# Automatically converts:
{"max_results": "5"}  # String → Integer
```

## Accessing Swagger Documentation

### 1. **Start the Server**
```bash
python api_server.py
```

### 2. **Open Swagger UI**
Open in browser:
```
http://localhost:8001/docs
```

### 3. **Alternative: ReDoc**
```
http://localhost:8001/redoc
```

## Swagger UI Features

1. **Interactive API Testing**
   - Try endpoints directly
   - See request/response examples
   - Test with different parameters

2. **Schema Documentation**
   - View all BaseModel classes
   - See field types and descriptions
   - Understand request/response structure

3. **Try It Out**
   - Click "Try it out" on any endpoint
   - Fill in parameters
   - Execute and see results

## Example: Using Swagger UI

1. Go to `http://localhost:8001/docs`
2. Find `/api/query` endpoint
3. Click "Try it out"
4. Enter:
   ```json
   {
     "text": "Who won IPL in 2025?",
     "thread_id": "test-123",
     "max_results": 5
   }
   ```
5. Click "Execute"
6. See the response!

## BaseModel in Your Code

### Current Models:

1. **QueryRequest** - Request body
   - `text`: User query (required)
   - `thread_id`: Conversation ID (optional)
   - `max_results`: Result limit (optional)

2. **SearchResult** - Individual search result
   - `title`, `url`, `content`, `score`, `timestamp`

3. **DataFreshness** - Data update info
   - `last_updated`, `source`, `result_count`

4. **QueryResponse** - API response
   - Contains all results, context, metadata

## Why Use BaseModel?

| Feature | Without BaseModel | With BaseModel |
|---------|------------------|----------------|
| Validation | Manual checks | Automatic |
| Documentation | Manual writing | Auto-generated |
| Type Safety | Runtime errors | Compile-time checks |
| API Docs | Separate files | Integrated |
| Error Messages | Generic | Detailed |

## Summary

- **BaseModel** = Data validation + Auto documentation
- **Swagger** = Interactive API documentation
- **FastAPI** = Automatically generates Swagger from BaseModel
- **Access** = `http://localhost:8001/docs`

Your API documentation is already available! Just start the server and visit `/docs`.

