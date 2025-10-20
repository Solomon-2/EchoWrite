# EchoWrite AI - LLM Configuration

## Usage Examples

Change model at runtime:
```python
from app.config.llm_config import update_model, get_llm

# Switch to faster model
update_model("llama-3.1-8b-instant")
llm = get_llm()

# Switch to larger model
update_model("llama-3.1-70b-versatile")
llm = get_llm()
```

Override settings for specific tasks:
```python
# Use higher temperature for creative content
creative_llm = get_llm(temperature=0.9)

# Use lower temperature for analytical tasks
analytical_llm = get_llm(temperature=0.3)
```

Check available models:
```python
from app.config.llm_config import get_available_models
print(get_available_models("groq"))
```