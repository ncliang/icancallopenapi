# I Can Call Open API

本專案嘗試用langchain結合Open AI Functions功能呼叫Open API。

# 使用API

> 由於智慧城鄉openapi.org.tw一直出現proxy error，申請帳號認證過程也不順利，因此使用中央氣象局API測試實作

使用中央氣象局API做範例
https://opendata.cwb.gov.tw/devManual/insrtuction

## 註冊氣象局帳號並取得API授權碼

使用本程式需先註冊中央氣象局會員帳號。註冊帳號之後取得API授權碼:
https://opendata.cwb.gov.tw/user/authkey

## 中央氣象局open API

https://opendata.cwb.gov.tw/dist/opendata-swagger.html#/

需要下載open API spec到本機
```
$ wget https://opendata.cwb.gov.tw/apidoc/v1
$ mv v1 cwb-v1.yaml
```
由於氣象局的spec為swagger 2.0格式，須先將其轉檔為openapi 3.0格式。可使用`https://editor.swagger.io/`進行轉檔

https://stackoverflow.com/a/59749691

`cwb-v1-openapi3.yaml`為轉檔為轉檔後之結果可供測試使用

# 使用方式

## 安裝
```
pip install -r requirements.txt
```

## 使用範例

問高雄市的天氣
```
(venv) ncliang@taipei:~/repos/icancallopenapi$ python icancallopenapi.py --api_key=xxxxx --spec_location=./cwb-v1-openapi3.yaml "高雄市的天氣"
...
output: 根據氣象資料，高雄市的天氣預報如下：

- 今天下午到晚上多雲時有短暫雷陣雨，溫度約為 22°C 至 32°C，降雨機率為 30%。
- 明天凌晨到白天多雲時有短暫陣雨，溫度約為 28°C 至 34°C，降雨機率為 30%。

請注意天氣變化，做好相應的準備。
```

換一種問法
```
(venv) ncliang@taipei:~/repos/icancallopenapi$ python icancallopenapi.py --api_key=xxxxx --spec_location=./cwb-v1-openapi3.yaml "高雄市明天會不會下雨"
...
output: 根據中央氣象局的預報，明天高雄市的天氣狀況如下：

- 白天（12:00-18:00）：多雲後短暫雷陣雨，溫度約為22°C。
- 晚上（18:00-06:00）：多雲短暫陣雨，溫度約為28°C。
- 早上（06:00-18:00）：多雲後短暫雷陣雨，溫度約為22°C。

降雨機率為30%。

請注意天氣變化，做好相應的準備。
```

問新北市的天氣
```
(venv) ncliang@taipei:~/repos/icancallopenapi$ python icancallopenapi.py --api_key=xxxxx --spec_location=./cwb-v1-openapi3.yaml "新北市的天氣"
...
output: 根據氣象資料，新北市的天氣預報如下：

- 今天下午到晚上多雲時陰，降雨機率為30%，最低溫度約26°C，最高溫度約31°C。
- 明天早上到下午多雲時陰，降雨機率為30%，最低溫度約26°C，最高溫度約34°C。

請注意天氣變化，做好相應的準備。
```

問中央氣象局沒有的資訊
```
(venv) ncliang@taipei:~/repos/icancallopenapi$ python icancallopenapi.py --api_key=xxxxx --spec_location=./cwb-v1-openapi3.yaml "新加坡的天氣"
...
output: 很抱歉，我無法取得新加坡的天氣資訊。請提供有效的地點。
```

問非天氣相關的資訊用其他tool回答
```
(venv) ncliang@taipei:~/repos/icancallopenapi$ python icancallopenapi.py --api_key=xxxxx --spec_location=./cwb-v1-openapi3.yaml "1024^2"
...
output: The value of 1024^2 is 1,048,576.
```

用`--verbose`參數觀察agent跟LLM對話過程
```
(venv) ncliang@taipei:~/repos/icancallopenapi$ python icancallopenapi.py --api_key=xxxxx --spec_location=./cwb-v1-openapi3.yaml "新北市的天氣" --verbose
Attempting to load an OpenAPI 3.0.1 spec.  This may result in degraded performance. Convert your OpenAPI spec to 3.1.* spec for better support.


> Entering new  chain...

Invoking: `CWB-Weather` with `新北市`




> Entering new  chain...

...
> Finished chain.
output: 根據氣象資料，新北市的天氣預報如下：

- 今天下午到晚上多雲時有短暫雷陣雨，溫度約為 22°C 至 31°C，降雨機率為 30%。
- 明天凌晨到白天時多雲，溫度約為 26°C 至 34°C，降雨機率為 10%。
- 明天下午到晚上多雲時有短暫雷陣雨，溫度約為 22°C 至 33°C，降雨機率為 30%。

請注意天氣變化，做好相應的準備。
```

# 參考資料
1. https://python.langchain.com/docs/modules/chains/additional/openapi
2. https://python.langchain.com/docs/modules/chains/additional/openapi_openai
3. https://python.langchain.com/docs/modules/agents/toolkits/openapi