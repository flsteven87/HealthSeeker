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
            {"role": "system", "content": "你是一位專業且經驗豐富的醫師，你的目標是完成主訴收集並且給予最後的診斷及建議，第一步，請先親切地引導病患完成專業的主訴收集，過程中你可以根據蒐集到的症狀，詢問他最可能有的其他症狀，來幫助你判斷他的病症，第二步請告訴他可能的病症或診斷結果，並且建議他去怎樣的科別就診。注意這是一個對話的過程，所以保持口語化，親切，一次只問一個題"}
        ]
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('user_input', '')
        request.session['messages'].append({"role": "user", "content": user_input})
        request.session.save()  # Explicitly save the session after appending message

        print(request.session['messages'])

        response = openai.ChatCompletion.create(
            # model="gpt-3.5-turbo-16k-0613",
            model="gpt-4-0613",
            messages=request.session['messages'],
            temperature=0
        )

        print(f"Prompt Token: {response['usage']['prompt_tokens']}.  Completion Tokens: {response['usage']['completion_tokens']}. Total tokens: {response['usage']['total_tokens']}")

        diagnosis = response['choices'][0]['message']['content']
        request.session['messages'].append({"role": "assistant", "content": diagnosis})
        request.session.save()  # Explicitly save the session after appending message

        return JsonResponse({'diagnosis': diagnosis})

    return JsonResponse({'error': 'Invalid request method'})
