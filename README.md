# QQ chatbot based on ChatGPT and go-cqhttp

### 介绍
基于ChatGPT和go-cqhttp的QQ聊天机器人，具有以下优点：
* 部署简易，无需配置编程环境
* 支持长对话记忆功能，可自定义记忆轮数和字数

### 前置准备
在进行部署前，需要准备好以下内容：
* 一个充当聊天机器人的QQ账号（有一定封号风险，请谨慎使用）
* 一个OpenAI账号以及对应的API Key

### 部署过程
1. 修改`go-cqhttp/config.yml`中的QQ号，注意不用填写密码
2. 修改`information.txt`中的QQ号、OpenAI账号、密码及API Key
3. 修改`information.txt`中的最大记忆轮数`maxRound`和最大记忆回复字数`maxLength`（可选）

### 使用方法
1. 运行`go-cqhttp/go-cqhttp.bat`并扫码登录QQ
2. 运行`main.exe`

### 拓展开发
在Python中按照`requirements.txt`安装依赖后，即可修改并运行源代码`main.py`。若需要将源代码打包为`.exe`文件，只需在终端输入以下指令即可：
```
pyinstaller -F main.py
```

### 参考项目
* [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
* [Qbot](https://github.com/zstar1003/Qbot)