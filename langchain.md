| Method                                      | Purpose                   | Response Type                        |
| ------------------------------------------- | ------------------------- | ------------------------------------ |
| llm.invoke()                                | Plain text generation     | AIMessage with content               |
| llm.bind_tools([...]).invoke()              | Can call tools (optional) | AIMessage with tool_calls or content |
| llm.with_structured_output(Schema).invoke() | Must follow schema        | Pydantic object (not AIMessage!)     |
| llm.bind(temp=0.5).invoke()                 | Pre-set parameters        | AIMessage with content               |

---

So in your case:

# These are DIFFERENT objects:

llm = init_chat_model("openai:gpt-4o-mini") # Base
llm_with_tools = llm.bind_tools(tools) # Augmented with tools
llm_structured = llm.with_structured_output(Schema) # Augmented with schema

    Synchronous methods:

| Method                  | Description                             | Returns            |
| ----------------------- | --------------------------------------- | ------------------ |
| invoke(messages)        | Complete response, wait for full result | AIMessage          |
| stream(messages)        | Stream response token-by-token          | Iterator of chunks |
| batch(list_of_messages) | Send multiple requests in batch         | List of AIMessage  |

Asynchronous methods (for concurrent operations):

| Method                   | Description             | Returns                       |
| ------------------------ | ----------------------- | ----------------------------- |
| ainvoke(messages)        | Async version of invoke | AIMessage (awaitable)         |
| astream(messages)        | Async streaming         | Async iterator                |
| abatch(list_of_messages) | Async batch processing  | List of AIMessage (awaitable) |
