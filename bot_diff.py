import requests 
import telebot 
import base64
import json

bot_token = 'TOKEN'
bot = telebot.TeleBot(bot_token)

URL = 'LINK TO GRADIO LIVE'
URL_txt2img = f'{URL}/sdapi/v1/txt2img'
URL_img2img = f'{URL}/sdapi/v1/img2img'

params_txt2img = {
  "enable_hr": False,
  "denoising_strength": 0,
  "firstphase_width": 0,
  "firstphase_height": 0,
  "hr_scale": 2,
  "hr_upscaler": "",
  "hr_second_pass_steps": 0,
  "hr_resize_x": 0,
  "hr_resize_y": 0,
  "prompt": "beautiful girl",
  "styles": [""],
  "seed": -1,
  "subseed": -1,
  "subseed_strength": 0,
  "seed_resize_from_h": -1,
  "seed_resize_from_w": -1,
  "sampler_name": "",
  "batch_size": 1,
  "n_iter": 1,
  "steps": 20,
  "cfg_scale": 7,
  "width": 512,
  "height": 512,
  "restore_faces": False,
  "tiling": False,
  "negative_prompt": "",
  "eta": 0,
  "s_churn": 0,
  "s_tmax": 0,
  "s_tmin": 0,
  "s_noise": 1,
  "override_settings": {},
  "override_settings_restore_afterwards": True,
  "script_args": [],
  "sampler_index": "Euler a"
}

params_img2img = {
  "init_images": ["NONE"],
  "resize_mode": 0,
  "denoising_strength": 0.75,
  "mask": "",
  "mask_blur": 4,
  "inpainting_fill": 0,
  "inpaint_full_res": True,
  "inpaint_full_res_padding": 0,
  "inpainting_mask_invert": 0,
  "initial_noise_multiplier": 0,
  "prompt": "",
  "styles": [""],
  "seed": -1,
  "subseed": -1,
  "subseed_strength": 0,
  "seed_resize_from_h": -1,
  "seed_resize_from_w": -1,
  "sampler_name": "",
  "batch_size": 1,
  "n_iter": 1,
  "steps": 20,
  "cfg_scale": 7,
  "width": 512,
  "height": 512,
  "restore_faces": False,
  "tiling": False,
  "negative_prompt": "",
  "eta": 0,
  "s_churn": 0,
  "s_tmax": 0,
  "s_tmin": 0,
  "s_noise": 1,
  "override_settings": {},
  "override_settings_restore_afterwards": True,
  "script_args": [],
  "sampler_index": "Euler",
  "include_init_images": False  
}
keywords = {'negative': 'negative_prompt', 'steps': 'steps', 'seed': 'seed', 'difference': 'denoising_strength', 'cfg': 'cfg_scale', 'batch': 'batch_size', 'h': 'height', 'w': 'width'}

last_prompts = {}


def CheckParams_txt2img(params: dict, chatId: int) -> bool:
  print(params)
  try:
    if (int)(params['steps']) <= 0 or (int)(params['steps']) > 30:
      bot.send_message(chatId, '*STEPS* amount should be greater than 0 and equal or less than 30', parse_mode='Markdown')
      return False
  except ValueError:
    bot.send_message(chatId, '*STEPS* should be an integer', parse_mode='Markdown')
    return False
  
  try:
    if (int)(params['cfg_scale']) < 1 or (int)(params['cfg_scale']) > 30:
      bot.send_message(chatId, '*CFG* value should be greater than 1 and equal or less than 30', parse_mode='Markdown')
      return False
  except ValueError:
    bot.send_message(chatId, '*CFG* should be an integer', parse_mode='Markdown')
    return False

  try:
    if (int)(params['batch_size']) < 1 or (int)(params['batch_size']) > 4:
      bot.send_message(chatId, '*BATCH* parameter value should be in range from 1 to 4', parse_mode='Markdown')
      return False
  except ValueError:
    bot.send_message(chatId, '*BATCH* should be integer', parse_mode='Markdown')
    return False
    
  try:
    if (int)(params['height']) > 600 or (int)(params['height']) < 50 or (int)(params['width']) > 600 or (int)(params['width']) < 50:
      bot.send_message(chatId, '*HEIGHT* and *WIDTH* parameters should be greater than 50 or equal or less than 600', parse_mode='Markdown')
      return False
  except ValueError:    
    bot.send_message(chatId, '*HEIGHT* and *WIDTH* should be integers', parse_mode='Markdown')
    return False

  
    
  return True


def Imagine_txt2img(chatId, params):
 
  if CheckParams_txt2img(params, chatId):    
    r = requests.post(URL_txt2img, json= params).json() 
    images = r['images']    
    images_text = [(str)(img) for img in images]
    images = [base64.b64decode(img) for img in images_text]
    for i in range(len(images)):
      bot.send_photo(chatId, images[i])
    msg_splitted = (str)(r['info']).split(sep=',')
    for i in range(len(msg_splitted)):
      if 'Seed:' in msg_splitted[i]:
        bot.send_message(chatId, msg_splitted[i])
  

def GetParams(text: str, type: str) -> dict:
  individual_params = None
  if type == 'txt2img':
    individual_params = params_txt2img.copy()  
  elif type == 'img2img':
    individual_params = params_img2img.copy()

  msg_splitted = text[8:].split('++')
  file = open('prompts.txt', 'a')
  file.write(text + '\n')
  file.close()

  individual_params['prompt'] = msg_splitted[0]

  for query_part in msg_splitted[1:]:
    for keyword in keywords:
        if keyword in query_part and keywords[keyword] in individual_params:
            individual_params[keywords[keyword]] = query_part[len(keyword) + 1:].strip()
            break

  return individual_params

@bot.message_handler(commands=['imagine'])
def Txt2Img(message):
  command = '/imagine'
  chatId = message.chat.id  
  if command in message.text:
    bot.send_message(chatId, 'Your image is generating... Wait...')       
    last_prompts[chatId]= message  
    params = GetParams(message.text, 'txt2img')      
    Imagine_txt2img(chatId, params)

@bot.message_handler(commands=['repeat'])
def RepeatPrompt(message):
  try:
    bot.reply_to(message, f'Your previous prompt was _{last_prompts[message.chat.id].text}_', parse_mode='Markdown')
    Txt2Img(last_prompts[message.chat.id])
  except KeyError: 
    bot.reply_to(message, f'You haven\'t made prompts so far!')
    
    
@bot.message_handler(commands=['help', 'start'])
def HelpMessage(message):
  info = f'Hello, dear *{message.from_user.username}*!\nYou can write _/imagine YOUR-PROMPT_ and bot will generate an image!\n\
You can also write _/repeat_ to repeat the last prompt you sent\n\n\
        *Available settings*:\n👉_++negative YOUR-PROMPT_ -- adds negative weights to your query\n👉_++steps AMOUNT_ -- specifies amount of steps to generate an image(in range from 1 to 30)\n\
👉_++seed VALUE_ -- specifies the initial seed of generation(by default it\'s -1 which means random seed)\n👉_++h HEIGHT_ -- specifies the height of an image(between 50 and 600 px)\n\
👉_++w WIDTH_ -- specifies the width of an image(between 50 and 600)\n👉_++cfg VALUE_ -- specifies how close bot follows the prompt. Low means the ai is more creative\n\
👉_++batch VALUE_ -- specifies the amount of images to generate(up to 4)\n\n\n\
*Example*:\n\
_/imagine the most attractive girl from university ++negative long hair, blonde ++steps 25 ++h 600 ++w 300 ++cfg 10 ++seed -1 ++batch 4_'
  bot.send_message(message.chat.id, info, parse_mode='Markdown')

bot.infinity_polling()


'''
Img2Img doesn't work right now

@bot.message_handler(content_types=['photo'])
def Img2Img(message):
  command = '/imagine'
  chatId = message.chat.id
  if command in message.caption:
    bot.send_message(chatId, 'Your image is generating... Wait...')
    params = GetParams(message.caption, 'img2img')
    if CheckParams_img2img(params, chatId):
      img_info = bot.get_file(message.photo[-1].file_id)
      img = bot.download_file(img_info.file_path)
      img_encoded = [base64.b64encode(img).decode("utf8")]      
      #img_decoded = base64.b64decode(img_encoded[0])
      
      params['init_images'] = img_encoded
      Imagine_img2img(chatId, params)


def Imagine_img2img(chatId, params):
  if CheckParams_img2img(params, chatId):
    try:
      r = requests.post(URL_img2img, json= params).json()   
    except json.decoder.JSONDecodeError or requests.exceptions.JSONDecodeError:
      bot.send_message(chatId, 'Server error')       
    image_text = (str)(r['images'])
    image = base64.b64decode(image_text)
    bot.send_photo(chatId, image)
   

def CheckParams_img2img(params: dict, chatId: int) -> bool:
  try:
    if (float)(params['denoising_strength']) > 1 or (float)(params['denoising_strength']) < 0:
      bot.send_message(chatId, '*DIFFERENCE* parameter should be greater than 0 and equal or less than 1', parse_mode='Markdown')
      return False
  except ValueError:
    bot.send_message(chatId, '*DIFFERENCE* parameter should be number between 0 and 1', parse_mode='Markdown')
    return False

  return True

'''

