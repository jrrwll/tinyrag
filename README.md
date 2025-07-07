## Tiny RAG

A Tiny Agent Workflow AI Application

### Features

- RAG
- Customize Tools


## How to

### startup the project

```shell
uv init
uv add fastapi uvicorn gunicorn sqlmodel pydantic pydantic-settings pymysql

# mypy: static type check
# ruff: code smell check
uv add --dev pytest mypy ruff coverage

uv add langchain langgraph langchain_ollama langchain_openai

uv add cachetools types-cachetools
```

### run the project

```sql
create database tinyrag;
create user 'tinyrag'@'%' identified by 'tinyrag';
grant all privileges on tinyrag.* to 'tinyrag'@'%';
```

```shell
cp .env.example .env

export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env

#export ENVIRONMENT=production

uv sync
source .venv/bin/activate

# or just run: pytest
./scripts/test.sh
```

```shell
# on local machine
./scripts/run.sh

# on production machine
./scripts/build_docker.sh

curl http://localhost:8000/api/v1/openapi.json
```

## Demo

**Demo 1**：[workflow_demo1.json](dev/http/workflow_demo1.json)

![alt](https://quickchart.io/graphviz?graph=digraph+G+%7B%0A++n1+%5Bstyle%3Dfilled%2Cshape%3DMsquare%2Clabel%3D%22%3Cstart%3E+Start+Node%0A%0Aquery%3A+text+%3D+%27%E8%BE%93%E5%85%A5%E6%96%87%E6%9C%AC%27%22%5D%0A++n2+%5Bshape%3Dbox%2Clabel%3D%22%3Cllm%3E+LLM+Node%0A%0Amodel+%3D+1%0Auser_prompt+%3D+%60%60%60%0A%7Bquery%7D%0A%60%60%60%0Aquestion%3A+str+%3D+%27%E4%BD%A0%E5%8F%8D%E9%97%AE%E7%94%A8%E6%88%B7%E7%9A%84%E9%97%AE%E9%A2%98%27%0Aanswer%3A+str+%3D+%27%E4%BD%A0%E7%9A%84%E5%9B%9E%E7%AD%94%27%22%5D%0A++n3+%5Bshape%3Dbox%2Clabel%3D%22%3Cllm%3E+LLM+Node2%0A%0Amodel+%3D+1%0Auser_prompt+%3D+%60%60%60%0A%E7%94%A8%E6%88%B7%E6%8F%90%E9%97%AE%EF%BC%9A%7Bquery%7D%0A%0AAI%E5%8A%A9%E6%89%8B%E7%9A%84%E5%9B%9E%E7%AD%94%EF%BC%9A%7Banswer%7D%0A%0A%E8%AF%B7%E8%AF%84%E4%BC%B0%E8%AF%A5AI%E5%8A%A9%E6%89%8B%E7%9A%84%E5%9B%9E%E7%AD%94%E6%98%AF%E5%90%A6%E5%87%86%E7%A1%AE%EF%BC%8C%E5%92%8C%E5%9B%9E%E7%AD%94%E8%AF%A5%E5%8A%A9%E6%89%8B%E5%8F%8D%E9%97%AE%E7%9A%84%E9%97%AE%E9%A2%98%EF%BC%9A%7Banswer%7D%0A%60%60%60%0Ascore%3A+int+%3D+%27%E5%9B%9E%E7%AD%94%E6%98%AF%E5%90%A6%E5%87%86%E7%A1%AE%EF%BC%8C%E8%AF%84%E5%88%86%E4%BB%8E1-10%EF%BC%8C10%E8%A1%A8%E7%A4%BA%E9%9D%9E%E5%B8%B8%E5%87%86%E7%A1%AE%27%0Aanswer%3A+str+%3D+%27%E4%BD%A0%E7%BB%99%E5%87%BA%E7%9A%84%E7%AD%94%E6%A1%88%EF%BC%8C%E7%94%A8%E4%BA%8E%E5%9B%9E%E7%AD%94AI%E5%8A%A9%E6%89%8B%E5%8F%8D%E9%97%AE%E7%9A%84%E9%97%AE%E9%A2%98%27%22%5D%0A++n4+%5Bshape%3Dbox%2Clabel%3D%22%3Cend%3E+End+Node%0A%0A++query+%3D+query%0A++query_answer+%3D+answer%0A++query_answer_score+%3D+score%0A++ai_query_answer+%3D+2.answer%22%5D%0A++n2+-%3E+n3%0A++n1+-%3E+n2%0A++n3+-%3E+n4%0A%0A%7D)

**Demo 2**：[workflow_demo2.json](dev/http/workflow_demo2.json)

![alt](https://quickchart.io/graphviz?graph=digraph+G+%7B%0A++n1+%5Bstyle%3Dfilled%2Cshape%3DMsquare%2Clabel%3D%22%3Cstart%3E+Start+Node%0A%0Amy_text%3A+text+%3D+%27%E8%BE%93%E5%85%A5%E6%96%87%E6%9C%AC%27%0Amy_number%3A+number+%3D+%27%E8%BE%93%E5%85%A5%E6%95%B0%E5%AD%97%27%0Amy_option%3A+option%0Amy_files%3A+files%22%5D%0A++n2+%5Bshape%3Dbox%2Clabel%3D%22%3Cllm%3E+LLM+Node%0A%0Amodel+%3D+1%0Auser_prompt+%3D+%60%60%60%0A%7Bmy_text%7D+%E6%98%AF%E5%A5%BD%E8%AF%84%E8%BF%98%E6%98%AF%E5%B7%AE%E8%AF%84%0A%60%60%60%0Agood%3A+str+%3D+%27%E5%A5%BD%E8%AF%84%E8%BE%93%E5%87%BAY%EF%BC%8C%E5%B7%AE%E8%AF%84%E8%BE%93%E5%87%BAN%27%0Agood_reason%3A+str+%3D+%27%E5%A5%BD%E8%AF%84%E5%B7%AE%E8%AF%84%E7%9A%84%E5%88%A4%E6%96%AD%E4%BE%9D%E6%8D%AE%27%22%5D%0A++n3+%5Bshape%3Dbox%2Clabel%3D%22%3Chttp%3E+Exception+Node%0Ahttp_config+%3D+%60%60%60%0A%7B%0A++%27method%27%3A+%27POST%27%2C%0A++%27url%27%3A+%27http%3A%2F%2F%7B%7BOLLAMA_HOST%7D%7D%3A11434%2Fapi%2Ftags%27%2C%0A++%27headers%27%3A+%7B%0A++++%27Content-Type%27%3A+%27application%2Fjson%27%0A++%7D%2C%0A++%27params%27%3A+null%2C%0A++%27json_body%27%3A+%27%7B%5Cn++++++++++++++%5C%27message%5C%27%3A+%5C%27%7Bmy_text%7D%5C%27%5Cn++++++++++++%7D%27%0A%7D%0A%60%60%60%22%5D%0A++n4+%5Bshape%3Dbox%2Clabel%3D%22%3Ccode%3E+Code+Node%0A%0Acode+%3D+%60%60%60%0Adef+main%28arg1%3A+str%29+-%3E+list%5Bstr%5D%3A%0A++++body_obj+%3D+json.loads%28arg1%29%0A++++if+isinstance%28body_obj%2C+dict%29%3A%0A++++++++return+%5Bmodel%5B%27name%27%5D+for+model+in+body_obj%5B%27models%27%5D%5D%0A++++else%3A%0A++++++++return+body_obj%0A%60%60%60%0A%0Acode_args+%3D+%5B%27body%27%5D%22%5D%0A++n5+%5Bshape%3Dbox%2Clabel%3D%22%3Ccondition%3E+Condition+Node%0A%0Aconditions+%3D+%27%7Bgood%7D+%3D%3D+%27Y%27%27%22%5D%0A++n6+%5Bshape%3Dbox%2Clabel%3D%22%3Cdoc_extract%3E+Doc+Extract+Node%0A%0Aextract_file+%3D+my_file%22%5D%0A++n7+%5Bshape%3Dbox%2Clabel%3D%22%3Cclassify%3E+Classify+Node%22%5D%0A++n8+%5Bshape%3Dbox%2Clabel%3D%22%3Ctemplate%3E+Template+Node%0A%0Atemplate+%3D+%60%60%60%0AThe+result+is+%7B%7Bclass_name%7D%7D%0A%60%60%60%0A%0A++class_name+%3D+7.class_name%22%5D%0A++n9+%5Bshape%3Dbox%2Clabel%3D%22%3Ctemplate%3E+Template+Node2%0A%0Atemplate+%3D+%60%60%60%0ANo+more+news+for+%7B%7Bclass_name%7D%7D%0A%60%60%60%0A%22%5D%0A++n10+%5Bshape%3Dbox%2Clabel%3D%22%3Cllm%3E+LLM+Node2%0A%0Amodel+%3D+1%0A%0A++text_output+%3D+text%22%5D%0A++n1+-%3E+n2%0A++n3+-%3E+n4%0A++n2+-%3E+n3%0A++n6+-%3E+n7%0A++n7+-%3E+n9%0A++n5+-%3E+n10%0A++n5+-%3E+n6%0A++n2+-%3E+n5%0A++n7+-%3E+n8%0A%0A%7D)
