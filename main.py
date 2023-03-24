import json
import requests
from flask import request, Flask
import openai

# 读取信息列表
f = open("information.txt")
lines = []
line = f.readline()
while line:
    lines.append(line.strip())
    line = f.readline()
print(lines)

cqhttp_url = "http://localhost:8700"  # CQ-http地址
qq_no = lines[1] # 机器人QQ号
openai_email = lines[3] # openai账号邮箱
openai_password = lines[5] # openai账号密码
openai.api_key = lines[7] # openai账号的apikey，在官网获取

identities = [] # 存储不同群聊
requirements = [] # 提问列表
responses = [] # chatgpt回复列表
maxRound = int(lines[9]) # 最大记忆对话轮数
maxLength = int(lines[11]) # 最大记忆回复字数

server = Flask(__name__)

def ask_gpt(requirements, responses):
    # 建立用于chatgpt对话的信息流
    messages = [{"role": "system", "content": "你是一个基于ChatGPT的QQ聊天机器人，能记忆" + str(maxRound) +
                                              "轮对话，每轮对话最多记忆" + str(maxLength) +
                                              "个字，并且可以通过“清空”指令来开启全新对话。"}]
    for i in range(len(requirements) - 1):
        messages.append({"role": "user", "content": requirements[i]})
        if i < len(responses):
            if len(responses[i]) > maxLength:
                responses[i] = responses[i][0:maxLength] # 如果回复字数超过最大限制，就只截取部分回复
            messages.append({"role": "assistant", "content": responses[i]})
    messages.append({"role": "user", "content": requirements[len(requirements) - 1]})
    print("当前信息流：")
    print(messages)
    # 调用api完成回复
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    result = json.loads(str(completion.choices[0].message))
    return result['content']

# 与ChatGPT交互
def chat(requirements, responses):
    # 尝试交互
    try:
        message = ask_gpt(requirements, responses)
        message = message.strip() # 去除空格和换行
        print("返回内容: ")
        print(message)
        return message
    # 交互失败，返回错误信息
    except Exception as error:
        print(error)
        message = '服务器未正常响应，原因：' + str(error)
        return message

# qq消息上报接口，qq机器人监听到的消息内容将被上报到这里
@server.route('/', methods=["POST"])
def get_message():
    if request.get_json().get('message_type') == 'group':  # 如果是群消息
        gid = request.get_json().get('group_id')  # 群号
        uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
        message = request.get_json().get('raw_message')  # 获取原始信息
        # 注意按群聊存储对话，每个群聊都有不同的对话列表
        if gid not in identities:
            identities.append(gid)
            print("identities: ")
            print(identities)
            requirements.append([])
            responses.append([])
        indexOfGid = identities.index(gid) # 获取当前群聊的索引
        # 判断当被@时才回答
        if str("[CQ:at,qq=%s]"%qq_no) in message:
            print("identity of current user: " + str(gid))
            requirements[indexOfGid].append(message)
            print("收到群聊消息：")
            print(requirements[indexOfGid][-1])
            # 若当前对话轮数超过最大限制，就清除最早的一轮对话
            if len(requirements[indexOfGid]) > maxRound:
                requirements[indexOfGid].pop(0)
                if len(responses[indexOfGid]) > 0:
                    responses[indexOfGid].pop(0)
            # 如果收到清空指令，就清空所有对话内容
            if requirements[indexOfGid][-1] == "[CQ:at,qq=" + qq_no + "] 清空":
                requirements[indexOfGid].clear()
                responses[indexOfGid].clear()
                msg_text = str('[CQ:at,qq=%s]\n' % uid) + "好的，已开启全新对话！"
                send_group_message(gid, msg_text)
            # 回复提问
            else:
                msg_text = chat(requirements[indexOfGid], responses[indexOfGid])  # 将消息转发给ChatGPT处理
                responses[indexOfGid].append(msg_text)  # 记录机器人的回复
                msg_text = str('[CQ:at,qq=%s]\n'%uid) + str(msg_text)  # @发言人
                send_group_message(gid, msg_text)  # 将消息转发到群里
    return "ok"

# 发送群消息方法
def send_group_message(gid, message):
    try:
        res = requests.post(url=cqhttp_url + "/send_group_msg",
                            params={'group_id': int(gid), 'message': message}).json()
        if res["status"] == "ok":
            print("群消息发送成功")
        else:
            print("群消息发送失败，错误信息：" + str(res['wording']))
    except:
        print("群消息发送失败")

if __name__ == '__main__':
    server.run(port=7777, host='0.0.0.0')