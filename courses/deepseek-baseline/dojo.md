---
course: deepseek-baseline
title: DeepSeek V4 Flash Baseline
description: 10 smoke scenarios measuring base coding capability without skills
difficulty: smoke
model: deepseek-v4-flash
scenarios:
- id: ds-01
  name: Fix Python syntax error
  description: Fix missing colon in Python function definition
  tags:
  - python
  - syntax
  prompt: "Fix the syntax error in this Python function:\n\n```python\ndef greet(name)\n\
    \    return f\"Hello, {name}\"\n```\n"
  expected_behaviors:
  - 'def greet(name):'
  - greet(name)
  judge_criteria:
  - Code compiles without syntax errors
  - greet('World') returns 'Hello, World'
- id: ds-02
  name: TypeScript type annotations
  description: Add type annotations to an untyped TypeScript function
  tags:
  - typescript
  - types
  prompt: "Add proper TypeScript type annotations to this untyped function:\n\n```typescript\n\
    function calculateTotal(items, taxRate) {\n  return items.reduce((sum, item) =>\
    \ {\n    return sum + item.price * item.quantity;\n  }, 0) * (1 + taxRate);\n\
    }\n```\n"
  expected_behaviors:
  - ': number'
  - ': string'
  judge_criteria:
  - TypeScript compiles with strict mode and no errors
  - 'Correctly infers or declares item shape with price: number and quantity: number'
- id: ds-03
  name: JavaScript async/await conversion
  description: Convert Promise .then() chain to async/await syntax
  tags:
  - javascript
  - async
  prompt: "Convert this Promise chain to use async/await:\n\n```javascript\nfunction\
    \ fetchUserData(userId) {\n  return fetch(`/api/users/${userId}`)\n    .then(response\
    \ => {\n      if (!response.ok) throw new Error('Network error');\n      return\
    \ response.json();\n    })\n    .then(data => {\n      return fetch(`/api/users/${data.teamId}/members`);\n\
    \    })\n    .then(res => res.json())\n    .catch(err => console.error('Failed:',\
    \ err));\n}\n```\n"
  expected_behaviors:
  - async function
  - await fetch
  judge_criteria:
  - Uses async keyword on function declaration
  - Uses await for each fetch call
  - Uses try/catch instead of .catch()
- id: ds-04
  name: SQL injection prevention
  description: Fix a SQL query vulnerable to injection by using parameterized queries
  tags:
  - python
  - sql
  - security
  prompt: "Fix the SQL injection vulnerability in this Python function. Use parameterized\
    \ queries.\n\n```python\nimport sqlite3\n\ndef get_user_by_email(email):\n   \
    \ conn = sqlite3.connect('users.db')\n    cursor = conn.cursor()\n    query =\
    \ f\"SELECT id, name, email FROM users WHERE email = '{email}'\"\n    cursor.execute(query)\n\
    \    return cursor.fetchone()\n```\n"
  expected_behaviors:
  - '?'
  - execute(
  judge_criteria:
  - No string concatenation or f-string in SQL query
  - Uses ? placeholder and passes email as execute() argument
  - Query logic and return value remain unchanged
- id: ds-05
  name: Python import reorganization
  description: Sort and reorganize imports according to PEP8 conventions
  tags:
  - python
  - style
  prompt: 'Reorganize these Python imports following PEP8 convention (standard library,
    third-party, local):


    ```python

    import json

    from datetime import datetime

    import os

    import sys

    import requests

    from flask import Flask, request

    from myproject.utils.helpers import format_date

    from myproject.models import User

    import numpy as np

    ```

    '
  expected_behaviors:
  - import json
  - import sys
  - import requests
  judge_criteria:
  - Standard library imports come first (json, datetime, os, sys)
  - Third-party imports next (flask, numpy, requests)
  - Local imports last (myproject)
  - Groups separated by blank lines
- id: ds-06
  name: Go nil check
  description: Add nil check before dereferencing a pointer in Go
  tags:
  - go
  - safety
  prompt: "Add a nil check before dereferencing the pointer in this Go function:\n\
    \n```go\ntype Config struct {\n  Port int\n  Timeout time.Duration\n}\n\nfunc\
    \ StartServer(cfg *Config) error {\n  port := cfg.Port\n  timeout := cfg.Timeout\n\
    \  listener, err := net.Listen(\"tcp\", fmt.Sprintf(\":%d\", port))\n  if err\
    \ != nil {\n    return err\n  }\n  return http.Serve(listener, nil)\n}\n```\n"
  expected_behaviors:
  - cfg == nil
  - if cfg
  judge_criteria:
  - Checks if cfg == nil before dereferencing
  - Returns an error (not panic) when cfg is nil
  - Original logic preserved when cfg is non-nil
- id: ds-07
  name: Go error handling
  description: Handle an ignored error return value in Go
  tags:
  - go
  - error-handling
  prompt: "Fix the ignored error in this Go function:\n\n```go\nimport (\n  \"io\"\
    \n  \"os\"\n)\n\nfunc CopyFile(src, dst string) error {\n  source, err := os.Open(src)\n\
    \  if err != nil {\n    return err\n  }\n  defer source.Close()\n\n  destination,\
    \ err := os.Create(dst)\n  if err != nil {\n    return err\n  }\n  defer destination.Close()\n\
    \n  io.Copy(destination, source)\n  return nil\n}\n```\n"
  expected_behaviors:
  - io.Copy
  - err
  judge_criteria:
  - io.Copy error is assigned to a variable
  - Error is checked and returned
  - Close is still deferred correctly
- id: ds-08
  name: React stale closure
  description: Fix a stale closure bug in React's setInterval with useState
  tags:
  - react
  - javascript
  - hooks
  prompt: "Fix the stale closure bug in this React component. The counter should increment\
    \ every second.\n\n```jsx\nfunction Counter() {\n  const [count, setCount] = React.useState(0);\n\
    \n  React.useEffect(() => {\n    const id = setInterval(() => {\n      setCount(count\
    \ + 1);\n    }, 1000);\n    return () => clearInterval(id);\n  }, []);\n\n  return\
    \ <div>{count}</div>;\n}\n```\n"
  expected_behaviors:
  - setCount(
  - prev
  judge_criteria:
  - setCount receives a function instead of a value
  - Count increments correctly without stale values
  - No unnecessary re-creations of the interval
- id: ds-09
  name: Dockerfile optimization
  description: Improve Dockerfile layer caching for a Node.js app
  tags:
  - docker
  - devops
  prompt: 'Optimize this Dockerfile for better layer caching. Package.json should
    change less often than source code.


    ```dockerfile

    FROM node:20-alpine

    WORKDIR /app

    COPY . .

    RUN npm install

    RUN npm run build

    EXPOSE 3000

    CMD ["npm", "start"]

    ```

    '
  expected_behaviors:
  - package
  - COPY
  - npm install
  judge_criteria:
  - COPY package*.json ./ comes before COPY . .
  - RUN npm install comes before COPY . .
  - Build and runtime steps are preserved
- id: ds-10
  name: Regex validation
  description: Write an email validation regex in Python
  tags:
  - python
  - regex
  prompt: "Write a function that validates email addresses using regex. The regex\
    \ should handle typical email formats:\n\n```python\nimport re\n\ndef is_valid_email(email:\
    \ str) -> bool:\n    # Write regex pattern here\n    pass\n```\n"
  expected_behaviors:
  - re.match
  - re.fullmatch
  - r"
  judge_criteria:
  - Matches user@example.com, a.b@domain.co, name+tag@company.org
  - Rejects missing @, missing domain, spaces in address
  - Uses re.match or re.fullmatch (not re.search without anchors)
---
