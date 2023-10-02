from django.shortcuts import render
import openai
from django.conf import settings
from django.http import JsonResponse
import json

# 初始化OpenAI API客戶端
openai.api_key = settings.OPENAI_API_KEY

def home(request):
    request.session.flush()  # Clear the session
    initial_message = "您好，請告訴我你哪裡不舒服？"
    return render(request, 'diagnosis/diagnosis.html', {"title": "HealthSeeker 健康尋醫", "initial_message": initial_message})

def diagnosis(request):
    if 'messages' not in request.session:
        request.session['messages'] = [
            {"role": "system", "content": "你是一位專業且經驗豐富的醫師，你的目標是完成主訴收集並且給予最後的診斷及建議，第一步，請先親切地引導病患完成專業的主訴收集，過程中你可以根據蒐集到的症狀，詢問他最可能有的其他症狀，來幫助你判斷他的病症，第二步請告訴他可能的病症或診斷結果，並且建議他去怎樣的科別就診。注意這是一個對話的過程，所以保持口語化，親切，一次只問一個題。若你覺得你已經能夠推薦他某個科別的醫療院所，請在最後加上 ===是==="}
        ]
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('user_input', '')
        request.session['messages'].append({"role": "user", "content": user_input})
        request.session.save()  # Explicitly save the session after appending message

        print(request.session['messages'])

        # model = "gpt-3.5-turbo-16k-0613"
        # model = "gpt-4-0613",
        # print(model)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            # model="gpt-4-0613",
            # model=model,
            messages=request.session['messages'],
            temperature=0
        )

        print(f"Prompt Token: {response['usage']['prompt_tokens']}.  Completion Tokens: {response['usage']['completion_tokens']}. Total tokens: {response['usage']['total_tokens']}")
    
        diagnosis = response['choices'][0]['message']['content']

        if "===是===" in diagnosis:
            diagnosis = diagnosis.replace("===是===", "")  # 移除 "===是==="
            print('ChatGPT 認為可以推薦他診所了')
            registration = True
            # 在這裡，希望能夠pop出註冊的畫面
        else:
            registration = False

        request.session['messages'].append({"role": "assistant", "content": diagnosis})
        request.session.save()  # Explicitly save the session after appending message

        data = {
            "diagnosis": diagnosis,
            "register_required": registration,
        }

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request method'})

def register_endpoint(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        id_card = data.get('id_card')
        password = data.get('password')
        
        # 簡單地印出接收到的資料
        print("Received ID Card:", id_card)
        print("Received Password:", password)
        
        # 實際場合下，您會將資料存儲到資料庫或進行其他處理。
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})