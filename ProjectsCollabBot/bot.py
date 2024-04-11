import logging
from telegram import (Update,
                       InlineKeyboardButton,
                        InlineKeyboardMarkup,
                         ReplyKeyboardMarkup)

from telegram import (InlineQueryResultArticle,
                       InputTextMessageContent,
                         InlineKeyboardButton,
                           InlineKeyboardMarkup)

from telegram.ext import (InlineQueryHandler,
                          ApplicationBuilder,
                           ContextTypes,
                            CallbackQueryHandler,CallbackContext,
                             filters,
                              MessageHandler,
                               ApplicationBuilder,
                                CommandHandler,
                                 ContextTypes,
                                  ConversationHandler,
                                   CommandHandler)
import difflib
import datetime
import asyncio
import os, json, time, threading
import random
import bot_statics as bot_statics
from PIL import Image
from typing import List
from datetime import timedelta
import traceback
import binascii
from telegram import Invoice, LabeledPrice
import base64

import requests
# Load environment variables
import django
from django.conf import settings
from asgiref.sync import sync_to_async
from django.utils import timezone

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ProjectsCollab.models import Post, User, User_Feedback, Transaction_Receipt
from rest_framework.renderers import JSONRenderer
from asgiref.sync import sync_to_async
from TonTools import *

# from pycryptodome.PublicKey import RSA
# from web3 import Web3
# from tronapi import Tron
from tronpy import Tron
# from .init import client
# from .wallet import wallet
import ton
from decimal import Decimal


import openai
openai.api_key = "----------"


# from tronapi.exceptions import AddressNotFound
try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


MENU, OFFER_NEW_SERVICES, OFFER_NEW_SERVICES_POST, OFFER_NEW_SERVICES_PRICE, SUBMIT_OFFER, PAYMENT, VIEW_SUMBMITED_OFFER_SERVICES, CONTACT_AND_SUPPORT, REPORT, COMMENTS_AND_SUGGESTIONS, TERMS_AND_CONDITIONS, WALLET_CONTENT, DEDUCT_CREDIT ,DONATIONS = range(14)
#----------------------------

PROJECTSCOLLAB_CHANNEL_ID = "----------"

EACH_CHANNEL_POST_PRICE = 1
JOB_QUEUE_FORMAT = '{}' 
RECEIPT_PENDING_TIME = 60*10
FREE_USER_CREDIT = 1

#--------------------------------- 
def error_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
            print("---------")
            print(f"Error occurred at line {error_line}: {e}")
            print("---------")
    return wrapper


async def is_user_in_blacklist(update, context):
    user_id = update.effective_user.id
    user = User.objects.get(user_id=user_id)

    if user.user_is_blocked == True:
        blocked_text = bot_statics.MESSAGES['START']['BLOCK']
        await update.message.reply_text(blocked_text, parse_mode='Markdown')
        return True
    else:
        return False

#--------------------------------- STATE-0 
@error_handler
async def start(update, context):
    
    wellcom_text = bot_statics.MESSAGES['START']['WELCOME']
    await update.message.reply_text(wellcom_text, parse_mode='Markdown')
    await register(update, context)
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_id = context.user_data['user_id']
        user = User.objects.get(user_id=user_id)
        if user.terms_accepted :
            await menu(update, context)
            return MENU
        else:
            await terms_and_conditions(update, context)
            return TERMS_AND_CONDITIONS
    

@error_handler
async def register(update, context):
    user_id = update.effective_user.id
    try:
        user = User.objects.get(user_id=user_id)
        context.user_data['user_id'] = user_id
    except:
        username = update.message.from_user.username
        chat_id = update.effective_chat.id
        user = User.objects.create(username=username,
                                    user_id=user_id,
                                      chat_id=chat_id,
                                      user_credit=FREE_USER_CREDIT)
        context.user_data['user_id'] = user_id

    return TERMS_AND_CONDITIONS


#--------------------------------- STATE-0 
@error_handler
async def terms_and_conditions(update, context):
    menu_buttons = [
        [bot_statics.BUTTONS['TERMS_AND_CONDITIONS']['CONDITIONS_ACCEPTANCE']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    conditions_text = bot_statics.MESSAGES['TERMS_AND_CONDITIONS']['CONDITIONS_CONTEXT']
    await update.message.reply_text(conditions_text,
                                     reply_markup=reply_markup,
                                       parse_mode='Markdown')
    return TERMS_AND_CONDITIONS


@error_handler
async def terms_and_conditions_handler(update, context):
    user_input = update.message.text  
    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)
    
    if user_input == bot_statics.BUTTONS['TERMS_AND_CONDITIONS']['CONDITIONS_ACCEPTANCE']:
        if user.terms_accepted == False:
            new_member_text = bot_statics.MESSAGES['START']['NEW_MEMBER']
            await context.bot.send_message(chat_id=user.user_id,
                                       text=new_member_text,
                                       parse_mode='Markdown')
        user.terms_accepted = True
        user.save()
   
        await menu(update, context)
        return MENU
    else:
        return TERMS_AND_CONDITIONS
   

#--------------------------------- STATE-1 | Menu
@error_handler  
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Define the buttons
    menu_buttons = [
        
        [bot_statics.BUTTONS['MENU']['SUBMIT_NEW_OFFER_SERVICES']],
        [bot_statics.BUTTONS['MENU']['VIEW_SUBMITED_OFFER_SERVICES']],
        [bot_statics.BUTTONS['MENU']['WALLET_CONTENT']],
        [bot_statics.BUTTONS['MENU']['CONTACT_AND_SUPPORT']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    manu_manual = bot_statics.MESSAGES['MENU']['MENU_MANUAL']
    await update.message.reply_text(manu_manual,
                                     reply_markup=reply_markup,
                                       parse_mode='Markdown')
    return MENU


@error_handler
async def menu_handler(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_input = update.message.text  
        if user_input == bot_statics.BUTTONS['MENU']['SUBMIT_NEW_OFFER_SERVICES']:
            if await offer_new_services(update, context):
                return OFFER_NEW_SERVICES
            else:
                return MENU
        elif user_input == bot_statics.BUTTONS['MENU']['VIEW_SUBMITED_OFFER_SERVICES']:
            await post_list(update, context)
            return VIEW_SUMBMITED_OFFER_SERVICES
        elif user_input == bot_statics.BUTTONS['MENU']['CONTACT_AND_SUPPORT']:
            await contact_and_support(update, context)
            return CONTACT_AND_SUPPORT
        elif user_input == bot_statics.BUTTONS['MENU']['WALLET_CONTENT']:
            await wallet_content(update, context)
            return WALLET_CONTENT


#--------------------------------- STATE-2 | Offer Services Handler
@error_handler
async def offer_new_services(update: Update, context: CallbackContext): 

    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)

    if user.posts.count() == 20:
        post_limit_text = "you reach the limit of posts"
        await update.message.reply_text(post_limit_text,
                                       parse_mode='Markdown')
        return False
    
    else:
        menu_buttons = [
            [bot_statics.BUTTONS['OFFER_NEW_SERVICES']['FREELANCER_OPTIONS'], bot_statics.BUTTONS['OFFER_NEW_SERVICES']['CLIENT_OPTIONS']],
            [bot_statics.BUTTONS['OFFER_NEW_SERVICES']['BACK_OPTION']],
        ]
        # Create a ReplyKeyboardMarkup object with the defined buttons
        reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                        one_time_keyboard=True,
                                            resize_keyboard=True)
        # Send a message with the buttons to the user
        offer_services_type_text = bot_statics.MESSAGES['OFFER_NEW_SERVICES']['OFFER_SERVICES_TYPE']
        await update.message.reply_text(offer_services_type_text,
                                        reply_markup=reply_markup,
                                        parse_mode='Markdown')
        return True


@error_handler
async def offer_new_services_handler(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_input = update.message.text  

        if user_input == bot_statics.BUTTONS['OFFER_NEW_SERVICES']['FREELANCER_OPTIONS']:
            context.user_data['service_type'] = '1'
            await offer_new_services_post(update, context)
            return OFFER_NEW_SERVICES_POST

        elif user_input == bot_statics.BUTTONS['OFFER_NEW_SERVICES']['CLIENT_OPTIONS']:
            context.user_data['service_type'] = '0'
            await offer_new_services_post(update, context)
            return OFFER_NEW_SERVICES_POST

        elif user_input == bot_statics.BUTTONS['OFFER_NEW_SERVICES']['BACK_OPTION']:
            await menu(update,context)
            return MENU

        return OFFER_NEW_SERVICES


#--------------------------------- STATE-2 | Offer Services Handler
@error_handler  
async def offer_new_services_post(update: Update, context: CallbackContext):
    menu_buttons = [
        [bot_statics.BUTTONS['OFFER_NEW_SERVICES_POST']['BACK_OPTION']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    enter_description_text = bot_statics.MESSAGES['OFFER_NEW_SERVICES_POST']['ENTER_CONTENT']
    await update.message.reply_text(enter_description_text,
                                     reply_markup=reply_markup,
                                       parse_mode='Markdown')
    return OFFER_NEW_SERVICES_POST


async def offer_new_services_post_handler(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_input = update.message.text  

        if user_input == bot_statics.BUTTONS['OFFER_NEW_SERVICES_POST']['BACK_OPTION']:
            await offer_new_services(update,context)
            return OFFER_NEW_SERVICES
        else:
            if len(user_input) > 1000:
                char_limit_text =  bot_statics.MESSAGES['GLOBAL']['TEXT_LIMIT']
                await update.message.reply_text(char_limit_text, parse_mode='Markdown')
            else:
                context.user_data['post_description'] = user_input
                await offer_new_services_price(update,context)
                return OFFER_NEW_SERVICES_PRICE
            
        return OFFER_NEW_SERVICES_POST
        

#--------------------------------- STATE-2 | Offer Services Handler
async def offer_new_services_price(update: Update, context: CallbackContext):
    menu_buttons = [
        [bot_statics.BUTTONS['OFFER_NEW_SERVICES_PRICE']['BACK_OPTION']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    enter_description_text = bot_statics.MESSAGES['OFFER_NEW_SERVICES_PRICE']['ENTER_FLOOR_PRICE']
    await update.message.reply_text(enter_description_text,
                                     reply_markup=reply_markup,
                                       parse_mode='Markdown')
    return OFFER_NEW_SERVICES_PRICE


async def offer_new_services_price_handler(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_input = update.message.text  

        if user_input == bot_statics.BUTTONS['OFFER_NEW_SERVICES_PRICE']['BACK_OPTION']:
            await offer_new_services_post(update,context)
            return OFFER_NEW_SERVICES_POST
        else:
            if len(user_input) > 500:
                char_limit_text = bot_statics.MESSAGES['GLOBAL']['TEXT_LIMIT']
                await update.message.reply_text(char_limit_text, parse_mode='Markdown')
            else:
                context.user_data['post_floor_price'] = user_input
                await submit_offer(update,context)
                return SUBMIT_OFFER
            
        return OFFER_NEW_SERVICES_PRICE


#--------------------------------- STATE-2 | Offer Services Handler
@error_handler  
async def submit_offer(update: Update, context: CallbackContext):

    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)
    post_owner = user    
    post_type = context.user_data['service_type']
    post_description = context.user_data['post_description']
    post_floor_price = context.user_data['post_floor_price']

    temp_post = Post(post_id='⭒⭒⭒⭒⭒⭒',
                        post_owner=post_owner,
                        post_type=post_type,
                        post_description = post_description,
                        post_floor_price = post_floor_price,
                        post_state='0',
                        suspicious_post_state='0',
                        in_channel=False,
                        # post_receipt=temp_transaction
                        )
    

    preview_text = bot_statics.MESSAGES['SUBMIT_OFFER']['PERVIEW_OF_POST'] 
    await update.message.reply_text(text=preview_text,parse_mode='Markdown')

    post_preview = await post_format(update, context, temp_post)
    await update.message.reply_text(text="{}".format(post_preview),parse_mode='HTML')
    menu_buttons = [
        [bot_statics.BUTTONS['SUBMIT_OFFER']['SUBMIT_OPTION']],
        [bot_statics.BUTTONS['SUBMIT_OFFER']['BACK_OPTION'], bot_statics.BUTTONS['SUBMIT_OFFER']['CANCEL_OPTION']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    review_text = bot_statics.MESSAGES['SUBMIT_OFFER']['REVIEW_POST']
    await update.message.reply_text(review_text,
                                     reply_markup=reply_markup,
                                       parse_mode='Markdown')
    return SUBMIT_OFFER


@error_handler  
async def submit_offer_handler(update, context):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_input = update.message.text  

        if user_input == bot_statics.BUTTONS['SUBMIT_OFFER']['BACK_OPTION']:
            await offer_new_services_price(update,context)
            return OFFER_NEW_SERVICES_PRICE

        elif user_input == bot_statics.BUTTONS['SUBMIT_OFFER']['CANCEL_OPTION']:
            cancel_confirmation_text = bot_statics.MESSAGES['SUBMIT_OFFER']['CANCEL_CONFIRMATION']
            await update.message.reply_text(cancel_confirmation_text, parse_mode='Markdown')
            await menu(update,context)
            return MENU

        elif user_input == bot_statics.BUTTONS['SUBMIT_OFFER']['SUBMIT_OPTION']:
            if await create_new_post(update,context) == False:
                await submit_offer(update,context)
                return SUBMIT_OFFER
            else:    
                await deduct_credit(update,context)
                return DEDUCT_CREDIT
    
        return SUBMIT_OFFER


#--------------------------------- STATE-2 | Offer Services Handler
async def deduct_credit(update: Update, context: CallbackContext):
    menu_buttons = [
        [bot_statics.BUTTONS['DEDUCT_CREDIT']['INCREASE_CREDIT']],
        [bot_statics.BUTTONS['DEDUCT_CREDIT']['BACK_TO_MENU_OPTION']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)
    pay_text = bot_statics.MESSAGES['DEDUCT_CREDIT']['SPEND_CREDIT'].format(int(user.user_credit))
    
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                    text=pay_text,
                                    reply_markup=reply_markup,
                                    parse_mode='Markdown')



    pay_button = bot_statics.BUTTONS['DEDUCT_CREDIT']['PAY_WITH_CREDIT']
    post_id = context.user_data['post']
    post = Post.objects.get(post_id=post_id)
    post_content = await post_format(update, context, post)

    change_state_button = [
        [InlineKeyboardButton(pay_button, callback_data='pay_with_credit {}'.format(post.post_id)),]
    ]
    reply_markup = InlineKeyboardMarkup(change_state_button)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                    text=post_content,
                                    reply_markup=reply_markup,
                                    parse_mode='HTML')

    return DEDUCT_CREDIT


@error_handler  
async def deduct_credit_handler(update, context):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_input = update.message.text  

        if user_input == bot_statics.BUTTONS['DEDUCT_CREDIT']['INCREASE_CREDIT']:
            await payment(update,context)
            return PAYMENT

        elif user_input == bot_statics.BUTTONS['DEDUCT_CREDIT']['BACK_TO_MENU_OPTION']:
            await menu(update,context)
            return MENU

        return DEDUCT_CREDIT


@error_handler
async def pay_with_credit(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        query = update.callback_query
        await query.answer()
        data = query.data.split(' ')

        # to_this_state = data[1]
        post_id = data[1]
        post = Post.objects.get(post_id=post_id)
        post_content = await post_format(update, context, post)


        user_id = context.user_data['user_id']
        user = User.objects.get(user_id=user_id)

        
        if user.user_credit >= EACH_CHANNEL_POST_PRICE:
            # post.post_owner.user_credit = user.user_credit
            await new_post_to_channel(update, context, post)
            
            resolve_button = bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['CHANGE_POST_STATE_TO_RESOLVED']
            in_progress_button = bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['CHANGE_POST_STATE_TO_IN_PROGRESS']
            next_post_state = resolve_button if post.post_state == '0' else in_progress_button
            change_state_button = [
                [InlineKeyboardButton(next_post_state,callback_data='change_post_state {}'.format(post_id)),]
                # InlineKeyboardButton('In Progress',callback_data='change_post_state_to in_progress {}'.format(post_id))]
            ]
            reply_markup = InlineKeyboardMarkup(change_state_button)
            await query.edit_message_text(post_content,
                                            reply_markup=reply_markup,
                                            parse_mode='HTML')

            return DEDUCT_CREDIT
        
        else:
            text = "your credit is not enogh. in crease your credit first."
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                            text=text,
                                            parse_mode='Markdown') 
            return DEDUCT_CREDIT


@error_handler
async def remove_post(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        query = update.callback_query
        await query.answer()
        data = query.data.split(' ')

        # to_this_state = data[1]
        post_id = data[1]
        post = Post.objects.get(post_id=post_id)
        post.delete()

        post_content = await post_format(update, context, post) + bot_statics.MESSAGES['VIEW_SUMBMITED_OFFER_SERVICES']['POST_IS_REMOVED']
        await query.edit_message_text(post_content,
                                parse_mode='HTML')

        return VIEW_SUMBMITED_OFFER_SERVICES

        
@error_handler
async def check_content_sensitivity(update: Update, context: CallbackContext, post):

    response =  await openai_access(update,context,post)
    if response.code == 'insufficient_quota':
        return True
    else:
        if 'Yes' in response.choices[0].message:
            post.suspicious_post_state = '1'
            post.save()
            return False
        else:
            return True
        

@error_handler
async def create_new_post(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_id = context.user_data['user_id']
        user = User.objects.get(user_id=user_id)

        post_owner = user   
        post_id = await generate_unique_id(update,context)
        post_type = context.user_data['service_type']
        post_description = context.user_data['post_description']
        post_floor_price = context.user_data['post_floor_price']
        expiration_date = timezone.now() + timedelta(seconds=RECEIPT_PENDING_TIME)


        new_post = Post.objects.create(post_id=post_id,
                            post_owner=post_owner,
                            post_type=post_type,
                            post_description = post_description,
                            post_floor_price = post_floor_price,
                            post_state='0',
                            suspicious_post_state='0',
                            in_channel=False,
                            payment_deadline=expiration_date)
        
        # name = JOB_QUEUE_FORMAT.format(post_id)    
        # context.job_queue.run_once(post_expiration, RECEIPT_PENDING_TIME, name=name)

        post_owner.posts.add(new_post)
        post_owner.save()
        
        context.user_data['post'] = new_post.post_id

        # await check_content_sensitivity(update, context, new_post)

        if new_post.suspicious_post_state == '1':
            suspicious_post_text = bot_statics.MESSAGES['DEDUCT_CREDIT']['SUSPICIOUS_POST']
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                    text=suspicious_post_text,
                                    parse_mode='Markdown') 
            return False
        else:
            return True


@error_handler
async def openai_access(update: Update, context: CallbackContext, post) :

    # client = openai.OpenAI()
    post_content = "content: \n" + post.post_description + "\n" + post.post_floor_price
    pre_command = "is this text sensitive content? answer just with Yes or No.\n\n"
    content = pre_command + post_content

    response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": content},
        ]
    )
    time.sleep(10)
    return response.json()


@error_handler
async def post_expiration(context: ContextTypes.DEFAULT_TYPE):

    post = Post.objects.get(post_id = context.job.name)

    if (timezone.now() > post.payment_deadline) and (post.in_channel == False):
        deadline = post.payment_deadline.strftime("%Y.%m.%d | %H:%M:%S")
        post_expriation_text = bot_statics.MESSAGES['GLOBAL']['POST EXPIRATION'] + deadline
        await context.bot.send_message(chat_id=post.post_owner.chat_id, text=post_expriation_text, parse_mode='Markdown')
        post.delete()

 
    # name = JOB_QUEUE_FORMAT.format(art.custom_id, collector.user_id)
    # jobs = context.job_queue.get_jobs_by_name(name=name)


#--------------------------------- STATE-2 | Offer Services Handler

@error_handler
async def payment(update: Update, context: CallbackContext): 

    menu_buttons = [
        [bot_statics.BUTTONS['PAYMENT']['DONATIONS']],
        [bot_statics.BUTTONS['PAYMENT']['BACK_TO_MENU_OPTION']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    back_to_menu_warning = bot_statics.MESSAGES['PAYMENT']['UNDER_CONSTRUCTION']
    await update.message.reply_text(back_to_menu_warning,
                                        reply_markup=reply_markup,
                                        parse_mode='Markdown')
    return PAYMENT

    ###### PAYMENT ---------------------
    # menu_buttons = [
    #     [statics.BUTTONS['PAYMENT']['BACK_TO_MENU_OPTION']],
    # ]
    # # Create a ReplyKeyboardMarkup object with the defined buttons
    # reply_markup = ReplyKeyboardMarkup(menu_buttons, 
    #                                    one_time_keyboard=True,
    #                                      resize_keyboard=True)
    # # Send a message with the buttons to the user
    # back_to_menu_warning = statics.MESSAGES['PAYMENT']['BACK_TO_MENU_WARNING'] +'\n'+ statics.MESSAGES['PAYMENT']['WALLET_ADDRESS'] +'\n'+ statics.MESSAGES['PAYMENT']['HASH_REQUEST']
    # await update.message.reply_text(back_to_menu_warning,
    #                                     reply_markup=reply_markup,
    #                                     parse_mode='Markdown')
    # return PAYMENT


@error_handler
async def payment_handler(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_input = update.message.text  
        if user_input == bot_statics.BUTTONS['PAYMENT']['BACK_TO_MENU_OPTION']:
            await menu(update,context)
            return MENU
        elif user_input == bot_statics.BUTTONS['PAYMENT']['DONATIONS']:
            await donations(update,context)
            return DONATIONS
        
        # return PAYMENT
        ###### PAYMENT ---------------------
        # else:
        #     transaction_validation = await check_transaction(update,context)
        #     if transaction_validation == True :
        #         await menu(update,context)
        #         return MENU
        #     else:
        #         invalid_transaction = bot_statics.MESSAGES['PAYMENT']['TRANSACTION_REJECTION']
        #         await update.message.reply_text(invalid_transaction, parse_mode='Markdown')
        #         return PAYMENT


@error_handler
async def check_transaction(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        transaction_validation_text = bot_statics.MESSAGES['PAYMENT']['TRANSACTION_VERIFICATION']
        pending_message = await update.message.reply_text(transaction_validation_text,
                                                            parse_mode='Markdown')
        user_id = context.user_data['user_id']
        user = User.objects.get(user_id=user_id)


        return False
    

#--------------------------------- STATE-2 | Offer Services Handler
@error_handler  
async def generate_unique_id(update: Update, context: CallbackContext):
    while True:
        # Generate a 6-digit random number
        new_id = str(random.randint(100000, 999999))
        # Check if the generated ID already exists in the database
        if not Post.objects.filter(post_id=new_id).exists():
            return new_id


@error_handler
async def post_format(update: Update, context: CallbackContext, post):
    # print("--------------------------")
    # print("New Post Details:")
    # print(f"Post ID: {post.post_id}")
    # print(f"Post Owner: {post.post_owner}")
    # print(f"Post Type: {post.post_type}")
    # print(f"Post Description: {post.post_description}")
    # print(f"Post State: {post.post_state}")
    # print(f"Suspicious Post State: {post.suspicious_post_state}")
    # print(f"In Channel: {post.in_channel}")
    # print("--------------------------")

    # post_type_symbol = '🅒' if int(post.post_type) == '0' else '🅕'
    post_type_str = 'Client' if int(post.post_type) == '0' else 'Freelancer'
    post_state_str = '☑️ In Progress'  if post.post_state == '0' else '✅ Resolved'
    suspicious_post_str = ''  if post.suspicious_post_state == '0' else '🚫 <b>Sensitive Content Detected.</b>'

    post_content = "├─ • Code:「 {} 」\n├─ • Type :「 #{} 」\n\n{}\n\n└─ • Floor Price: {}\n\n───────────────\n🆔 @{}\n{}\n───────────────\n@ProjectsCollabBot\n\n{}".format(
                                            # post_type_symbol,
                                            post.post_id,
                                            post_type_str,
                                            post.post_description,
                                            post.post_floor_price,
                                            post.post_owner.username,
                                            post_state_str,
                                            suspicious_post_str)


    return post_content


@error_handler  
async def new_post_to_channel(update: Update, context: CallbackContext, new_post):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        new_post_content = await post_format(update, context, new_post)
        message_in_channel = await context.bot.send_message(chat_id=PROJECTSCOLLAB_CHANNEL_ID, text=new_post_content, parse_mode='HTML')
        new_post.massage_id_in_channel = message_in_channel.message_id
        new_post.in_channel=True
        new_post.post_owner.user_credit = new_post.post_owner.user_credit - EACH_CHANNEL_POST_PRICE
        new_post.post_owner.save()
        new_post.save()

        send_post_to_channel_text = bot_statics.MESSAGES['PAYMENT']['SEND_POST_TO_CHANNEL'].format(int(new_post.post_owner.user_credit))
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                    text = send_post_to_channel_text,
                                        parse_mode='Markdown')
        return DEDUCT_CREDIT


#---------------------------------
@error_handler
async def generate_buttons(data_list, start_index, end_index, num_columns=3, num_rows=2):
    
    # Create buttons for each item in the current page
    page = data_list[start_index:end_index]
    buttons = []

    for i in range(0, len(page), num_columns):
        row_buttons = page[i:i + num_columns]
        row_button_objects = [] 
        for tx in row_buttons:
            if Post.objects.get(post_id=tx).in_channel == False:
                button = InlineKeyboardButton(text="{} {}".format('∘',tx), callback_data=f'{tx}')
            else:
                button = InlineKeyboardButton(text="{}".format(tx), callback_data=f'{tx}')
            row_button_objects.append(button)
        buttons.append(row_button_objects)

    # Add navigation buttons to separate rows
    navigation_buttons = [
        [InlineKeyboardButton(text=' ◁', callback_data='prev'),
        InlineKeyboardButton(text=' ∘ ', callback_data='unpaied'),
        InlineKeyboardButton(text=' ▷ ', callback_data='next')]
    ]
    buttons.extend(navigation_buttons)
    return buttons


@error_handler
async def post_list(update: Update, context: CallbackContext):
    menu_buttons = [
        [bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['INCREASE_CREDIT']],
        [bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['BACK_TO_MENU_OPTION']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)

    pay_text = bot_statics.MESSAGES['VIEW_SUMBMITED_OFFER_SERVICES']['ALL_POSTS'].format(int(user.user_credit))
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                    text=pay_text,
                                    reply_markup=reply_markup,
                                    parse_mode='Markdown')
    

    # post list 
    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)

    data_list = [post.post_id for post in user.posts.all()]
    post_list_message = bot_statics.MESSAGES['VIEW_SUMBMITED_OFFER_SERVICES']['POST_LIST']

    # Variable to keep track of the start and end indexes of the current page
    start_index = 0
    end_index = 6  # Show 3 items per page initially
    if len(data_list) <= end_index:
        end_index = len(data_list)
    step = 6

    if len(data_list) == 0:
        start_index = -1


    buttons = await generate_buttons(data_list, start_index, end_index)
    reply_markup = InlineKeyboardMarkup(buttons)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="{}\n\n{} - {} | *{}*".format(post_list_message, start_index + 1, end_index, len(data_list)),
        reply_markup=reply_markup,
        parse_mode='Markdown',
        protect_content = PROTECT_CONTENT
    )

    # Save the message ID and current page indexes to use them later
    context.user_data['message_id'] = message.message_id
    context.user_data['start_index'] = start_index
    context.user_data['end_index'] = end_index
    context.user_data['step'] = step
    
    return VIEW_SUMBMITED_OFFER_SERVICES


@error_handler
async def forward_buttons_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    query = update.callback_query
    await query.answer()

    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)

    data_list = [post.post_id for post in user.posts.all()]

    post_list_message = bot_statics.MESSAGES['VIEW_SUMBMITED_OFFER_SERVICES']['POST_LIST']
    # Retrieve the current page indexes
    start_index = context.user_data.get('start_index')
    end_index = context.user_data.get('end_index')
    step = context.user_data.get('step')
    # Move to the next page (increase indexes by 3)
    start_index += step
    end_index += step
    # Check if we have reached the end of the list
    if start_index >= len(data_list):
        return VIEW_SUMBMITED_OFFER_SERVICES
    
    if len(data_list) == 0:
        start_index = -1
    # Create buttons for the next page
    buttons = await generate_buttons(data_list, start_index, end_index)
    reply_markup = InlineKeyboardMarkup(buttons)
    # Edit the original message with the updated buttons and text for the next page
    show_end_index = len(data_list) if end_index >= len(data_list) else end_index
    await query.message.edit_text(
        "{}\n\n{} - {} | *{}*".format(post_list_message, start_index + 1, show_end_index, len(data_list)),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    # Update the user data with the new page indexes
    context.user_data['start_index'] = start_index
    context.user_data['end_index'] = end_index

    return VIEW_SUMBMITED_OFFER_SERVICES


@error_handler
async def backward_buttons_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    query = update.callback_query
    await query.answer()


    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)

    data_list = [post.post_id for post in user.posts.all()]
    post_list_message = bot_statics.MESSAGES['VIEW_SUMBMITED_OFFER_SERVICES']['POST_LIST']
    # Retrieve the current page indexes
    start_index = context.user_data.get('start_index')
    end_index = context.user_data.get('end_index')
    step = context.user_data.get('step')

    # Move to the previous page (decrease indexes by 3)
    start_index -= step
    end_index -= step
    # Check if we have reached the beginning of the list
    if end_index <= 0:
        return VIEW_SUMBMITED_OFFER_SERVICES
    
    if len(data_list) == 0:
        start_index = -1
    # Create buttons for the previous page
    buttons = await generate_buttons(data_list, start_index, end_index)
    reply_markup = InlineKeyboardMarkup(buttons)
    # Edit the original message with the updated buttons and text for the previous page
    await query.message.edit_text(
        "{}\n\n{} - {} | *{}*".format(post_list_message, start_index + 1, end_index, len(data_list)),
        reply_markup=reply_markup,
        parse_mode='Markdown'

    )
    # Update the user data with the new page indexes
    context.user_data['start_index'] = start_index
    context.user_data['end_index'] = end_index

    return VIEW_SUMBMITED_OFFER_SERVICES


async def unpaied(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)

    all_user_posts = user.posts.all()
    unpaied_posts = []
    for post in all_user_posts:
        if post.in_channel == False:
            unpaied_posts.append(post.post_id)

    if len(unpaied_posts) == 0:
        unpaied_posts_text = bot_statics.MESSAGES['VIEW_SUMBMITED_OFFER_SERVICES']['NO_NOT_IN_CHANNEL_POSTS'] 
    else:
        post_list_bullet = ["├─ ∘「 {} 」\n".format(up) for up in unpaied_posts[:len(unpaied_posts)-1] ]
        posts_bullet = "".join(post_list_bullet) + "└─ ∘「 {} 」\n".format(unpaied_posts[-1])
        unpaied_posts_text = bot_statics.MESSAGES['VIEW_SUMBMITED_OFFER_SERVICES']['NOT_IN_CHANNEL_POSTS'] + posts_bullet

    
    await query.message.reply_text(unpaied_posts_text,
                                    parse_mode='Markdown')

    return VIEW_SUMBMITED_OFFER_SERVICES


@error_handler
async def view_post(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        query = update.callback_query
        await query.answer()

        post_id = query.data
        post = Post.objects.get(post_id=post_id)
        post_content = await post_format(update, context, post)

        if post.suspicious_post_state == '1':
            await query.message.reply_text(post_content,
                                    parse_mode='HTML')
            return VIEW_SUMBMITED_OFFER_SERVICES
        else:
            if post.in_channel == False:
                pay_credit_button = bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['PAY_WITH_CREDIT']
                remove_post_button = bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['REMOVE_POST']

                change_state_button = [
                    [InlineKeyboardButton(pay_credit_button, callback_data='pay_with_credit {}'.format(post_id)),],
                    [InlineKeyboardButton(remove_post_button, callback_data='remove_post {}'.format(post_id)),]
                ]
                reply_markup = InlineKeyboardMarkup(change_state_button)

                await query.message.reply_text(post_content,
                                                reply_markup=reply_markup,
                                                parse_mode='HTML')
                
                return VIEW_SUMBMITED_OFFER_SERVICES
            else:
                resolve_button = bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['CHANGE_POST_STATE_TO_RESOLVED']
                in_progress_button = bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['CHANGE_POST_STATE_TO_IN_PROGRESS']

                next_post_state = resolve_button if post.post_state == '0' else in_progress_button

                change_state_button = [
                    [InlineKeyboardButton(next_post_state,callback_data='change_post_state {}'.format(post_id)),]
                    # InlineKeyboardButton('In Progress',callback_data='change_post_state_to in_progress {}'.format(post_id))]
                ]
                reply_markup = InlineKeyboardMarkup(change_state_button)

                await query.message.reply_text(post_content,
                                                reply_markup=reply_markup,
                                                parse_mode='HTML')
                return VIEW_SUMBMITED_OFFER_SERVICES
    

@error_handler
async def change_post_state(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        query = update.callback_query
        await query.answer()
        data = query.data.split(' ')

        # to_this_state = data[1]
        post_id = data[1]
        post = Post.objects.get(post_id=post_id)

        post.post_state = '1' if post.post_state == '0' else '0'
        post.save()

        await update_post_in_channel(update,context,post)

        resolve_button = bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['CHANGE_POST_STATE_TO_RESOLVED']
        in_progress_button = bot_statics.BUTTONS['VIEW_SUMBMITED_OFFER_SERVICES']['CHANGE_POST_STATE_TO_IN_PROGRESS']

        to_this_state = resolve_button if post.post_state == '0' else in_progress_button


        post_content = await post_format(update, context, post)
        change_state_button = [
            [InlineKeyboardButton('{}'.format(to_this_state),callback_data='change_post_state {}'.format(post_id))]
            # InlineKeyboardButton('In Progress',callback_data='change_post_state_to in_progress {}'.format(post_id))]
        ]
        reply_markup = InlineKeyboardMarkup(change_state_button)
        await query.message.edit_text("{}".format(post_content), reply_markup=reply_markup, parse_mode='HTML')

        return VIEW_SUMBMITED_OFFER_SERVICES


@error_handler
async def update_post_in_channel(update: Update, context: CallbackContext, post):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        message_id_in_channel = post.massage_id_in_channel
        post_content = await post_format(update,context, post)
        await context.bot.edit_message_text(chat_id=PROJECTSCOLLAB_CHANNEL_ID, 
                                            message_id=message_id_in_channel,
                                            text=post_content)
        return VIEW_SUMBMITED_OFFER_SERVICES
    

#---------------------------------
async def contact_and_support(update: Update, context: CallbackContext):
    menu_buttons = [
        [bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['COMMENTS_AND_SUGGESTIONS']],
        [bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['SCAM_REPORT'],
         bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['DONATIONS']],
        [bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['TERMS_AND_CONDITIONS']],
        [bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['BACK']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    contact_and_support_option_text = bot_statics.MESSAGES['CONTACT_AND_SUPPORT']['SUPPORT_OPTIONS']
    await update.message.reply_text(contact_and_support_option_text,
                                     reply_markup=reply_markup,
                                       parse_mode='Markdown')
    return CONTACT_AND_SUPPORT


async def contact_and_support_handler(update: Update, context: CallbackContext):
    user_input = update.message.text  

    if user_input == bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['COMMENTS_AND_SUGGESTIONS']:
        await comments_and_suggestions(update,context)
        return COMMENTS_AND_SUGGESTIONS

    elif user_input == bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['SCAM_REPORT']:
        await report(update,context)
        return REPORT

    elif user_input == bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['DONATIONS']:
        await donations(update,context)
        return DONATIONS
    
    elif user_input == bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['TERMS_AND_CONDITIONS']:
        await terms_and_conditions(update,context)
        return TERMS_AND_CONDITIONS
       
    elif user_input == bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['BACK']:
        await menu(update,context)
        return MENU
    
    return CONTACT_AND_SUPPORT


#---------------------------------
# @error_handler  
async def report(update: Update, context: CallbackContext):
    send_report_description_text = bot_statics.MESSAGES['CONTACT_AND_SUPPORT']['SEND_REPORT']
    
    menu_buttons = [
        [bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['BACK_TO_MENU_OPTION']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    await update.message.reply_text(send_report_description_text,
                                        reply_markup=reply_markup,
                                        parse_mode='Markdown')
                                        
    return REPORT


# @error_handler  
async def report_handler(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_input = update.message.text

        if user_input == bot_statics.BUTTONS['REPORT']['BACK_TO_MENU_OPTION']:
            await menu(update,context)
            return MENU
        else:
            if len(user_input) > 1000:
                char_limit_text = bot_statics.MESSAGES['GLOBAL']['TEXT_LIMIT']
                await update.message.reply_text(char_limit_text, parse_mode='Markdown')
            else:
                user_id = context.user_data['user_id']
                user = User.objects.get(user_id=user_id)

                report_feedback = User_Feedback.objects.create(feedback_content=user_input)
                report_feedback.save()

                user.user_reports.add(report_feedback)
                user.save()

                feedback_submition = bot_statics.MESSAGES['CONTACT_AND_SUPPORT']['FEEDBACAK_SUBMITED'] 
                await update.message.reply_text(feedback_submition, parse_mode='Markdown')
                
                await menu(update,context)
                return MENU
        
        return REPORT


#---------------------------------
async def comments_and_suggestions(update: Update, context: CallbackContext):
    send_comment_description_text = bot_statics.MESSAGES['CONTACT_AND_SUPPORT']['SEND_COMMENT']

    menu_buttons = [
        [bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['BACK_TO_MENU_OPTION']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    await update.message.reply_text(send_comment_description_text,
                                        reply_markup=reply_markup,
                                        parse_mode='Markdown')
                                        
    return COMMENTS_AND_SUGGESTIONS


async def comments_and_suggestions_handler(update: Update, context: CallbackContext):
    user_input = update.message.text

    if user_input == bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['BACK_TO_MENU_OPTION']:
        await menu(update,context)
        return MENU
    else:
        if len(user_input) > 1000:
            char_limit_text = bot_statics.MESSAGES['GLOBAL']['TEXT_LIMIT']
            await update.message.reply_text(char_limit_text, parse_mode='Markdown')
        else:
            user_id = context.user_data['user_id']
            user = User.objects.get(user_id=user_id)

            comment_feedback = User_Feedback.objects.create(feedback_content=user_input)
            comment_feedback.save()

            user.user_comments_and_suggestions.add(comment_feedback)
            user.save()


            feedback_submition = bot_statics.MESSAGES['CONTACT_AND_SUPPORT']['FEEDBACAK_SUBMITED'] 
            await update.message.reply_text(feedback_submition, parse_mode='Markdown')

            await menu(update,context)
            return MENU
    
    return COMMENTS_AND_SUGGESTIONS


#---------------------------------
async def donations(update: Update, context: CallbackContext):
    
    menu_buttons = [
        [bot_statics.BUTTONS['CONTACT_AND_SUPPORT']['BACK_TO_MENU_OPTION']],
    ] 
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    donation_text = bot_statics.MESSAGES['DONATIONS']['DONATIONS_DESCRIPTION']
    await update.message.reply_text(donation_text,
                                        reply_markup=reply_markup,
                                        parse_mode='Markdown')  
    


    donation_options_button = [
        [InlineKeyboardButton(bot_statics.BUTTONS['DONATIONS']['USTD_OPTION'], callback_data='ustd_donation'),
        InlineKeyboardButton(bot_statics.BUTTONS['DONATIONS']['TON_OPTION'], callback_data='ton_donation'),
        InlineKeyboardButton(bot_statics.BUTTONS['DONATIONS']['BITCOIN_OPTION'], callback_data='bitcoin_donation')]
    ]
    reply_markup = InlineKeyboardMarkup(donation_options_button)
    donation_options = bot_statics.MESSAGES['DONATIONS']['DONATIONS_PAYMENT_WAY']
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=donation_options,
                                    reply_markup=reply_markup,
                                    parse_mode='Markdown')

    return DONATIONS


async def donations_handler(update: Update, context: CallbackContext):
    user_input = update.message.text

    if user_input == bot_statics.BUTTONS['DONATIONS']['BACK_TO_MENU_OPTION']:
        await menu(update,context)
        return MENU
    return DONATIONS


async def ustd_donation(update: Update, context: CallbackContext):

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("./media/" + "ustd_qr.jpg", 'rb'),  
        caption=bot_statics.MESSAGES['DONATIONS']['DONATIONS_USTD_ADDRESS'], 
        parse_mode='Markdown',
    )

    return DONATIONS


async def ton_donation(update: Update, context: CallbackContext):
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("./media/" + "ton_qr.jpg", 'rb'),  
        caption=bot_statics.MESSAGES['DONATIONS']['DONATIONS_TON_ADDRESS'], 
        parse_mode='Markdown',
    )

    return DONATIONS


async def bitcoin_donation(update: Update, context: CallbackContext):
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("./media/" + "bitcoin_qr.jpg", 'rb'),  
        caption=bot_statics.MESSAGES['DONATIONS']['DONATIONS_BITCOIN_ADDRESS'], 
        parse_mode='Markdown',
    )

    return DONATIONS

#---------------------------------
async def wallet_content(update: Update, context: CallbackContext):

    user_id = context.user_data['user_id']
    user = User.objects.get(user_id=user_id)
   # Define the buttons
    menu_buttons = [
        [bot_statics.BUTTONS['WALLET_CONTENT']['INCREASE_CREDIT']],
        [bot_statics.BUTTONS['WALLET_CONTENT']['BACK_TO_MENU_OPTION']],
    ]
    # Create a ReplyKeyboardMarkup object with the defined buttons
    reply_markup = ReplyKeyboardMarkup(menu_buttons, 
                                       one_time_keyboard=True,
                                         resize_keyboard=True)
    # Send a message with the buttons to the user
    user_wallet_content = bot_statics.MESSAGES['WALLET_CONTENT']['WALLET_CONTENT_CREDIT'].format(int(user.user_credit))
    await update.message.reply_text(user_wallet_content,
                                     reply_markup=reply_markup,
                                       parse_mode='Markdown')
    return WALLET_CONTENT


async def wallet_content_handler(update: Update, context: CallbackContext):
    if await is_user_in_blacklist(update, context) == True:
        return None 
    else:
        user_input = update.message.text
        if user_input == bot_statics.BUTTONS['WALLET_CONTENT']['BACK_TO_MENU_OPTION']:
            await menu(update,context)
            return MENU
        elif user_input == bot_statics.BUTTONS['WALLET_CONTENT']['INCREASE_CREDIT']:
            await payment(update,context)
            return PAYMENT


#---------------------------------
def reschedule_auctions(job_queue):

    async def server_status(context: ContextTypes.DEFAULT_TYPE):
        admin = "----------"
        current_time = datetime.now().strftime("%Y.%m.%d | %H:%M:%S")
        await context.bot.send_message(chat_id=admin,
                                  text="*⊘ Server Status*\n* • Current Status:* UP\n* • Time:* {}".format(current_time),
                                  parse_mode='Markdown')
        print("Server Check: OK")
        return True
    job_queue.run_repeating(server_status, 6*60*60)


    # out_of_channel_posts = Post.objects.filter(in_channel=False)
    # for post in out_of_channel_posts:
    #     expiration_date = timezone.now() + timedelta(seconds=RECEIPT_PENDING_TIME)
    #     post.payment_deadline = expiration_date
    #     name = JOB_QUEUE_FORMAT.format(post.post_id)
    #     # remain_auction_time = art.auction_end_time - timezone.now()
    #     job_queue.run_once(post_expiration, RECEIPT_PENDING_TIME, chat_id=post.post_owner.chat_id, user_id=post.post_owner.user_id, name=name)

    # return 


#---------------------------------
def main() -> None:

    TOKEN = "----------"

    application = ApplicationBuilder().token(TOKEN).build()
    job_queue = application.job_queue

    reschedule_auctions(job_queue)


    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TERMS_AND_CONDITIONS:[
                MessageHandler(filters.TEXT & ~ filters.COMMAND, terms_and_conditions_handler),
            ],
            MENU: [
                MessageHandler(filters.TEXT & ~ filters.COMMAND, menu_handler),
            ],
            OFFER_NEW_SERVICES: [ 
                MessageHandler(filters.TEXT & ~ filters.COMMAND, offer_new_services_handler),
            ],
            OFFER_NEW_SERVICES_POST: {               
                MessageHandler(filters.TEXT & ~ filters.COMMAND, offer_new_services_post_handler),
            },
            OFFER_NEW_SERVICES_PRICE:{
                MessageHandler(filters.TEXT & ~ filters.COMMAND, offer_new_services_price_handler),
            },
            SUBMIT_OFFER:{
                MessageHandler(filters.TEXT & ~ filters.COMMAND, submit_offer_handler),
            },
            DEDUCT_CREDIT:{
                CallbackQueryHandler(pay_with_credit, r'^pay_with_credit \d{6}$'),
                CallbackQueryHandler(change_post_state, r'^change_post_state \d{6}$'),

                MessageHandler(filters.TEXT & ~ filters.COMMAND, deduct_credit_handler),
            },
            PAYMENT: {
                MessageHandler(filters.TEXT & ~ filters.COMMAND, payment_handler),
            },
            VIEW_SUMBMITED_OFFER_SERVICES: [  
                CallbackQueryHandler(forward_buttons_action, pattern=r'^next$'),
                CallbackQueryHandler(unpaied, pattern=r'^unpaied$'),
                CallbackQueryHandler(backward_buttons_action, pattern=r'^prev$'),

                CallbackQueryHandler(view_post, r'^\d{6}$'),
                CallbackQueryHandler(pay_with_credit, r'^pay_with_credit \d{6}$'),
                CallbackQueryHandler(remove_post, r'^remove_post \d{6}$'),
                CallbackQueryHandler(change_post_state, r'^change_post_state \d{6}$'),

                MessageHandler(filters.TEXT & ~ filters.COMMAND, deduct_credit_handler),
            ],
            WALLET_CONTENT:[
                MessageHandler(filters.TEXT & ~ filters.COMMAND, wallet_content_handler),
            ],
            CONTACT_AND_SUPPORT:[
                MessageHandler(filters.TEXT & ~ filters.COMMAND, contact_and_support_handler),
            ],
            COMMENTS_AND_SUGGESTIONS: [
                MessageHandler(filters.TEXT & ~ filters.COMMAND, comments_and_suggestions_handler),
            ],  
            REPORT: [ 
                MessageHandler(filters.TEXT & ~ filters.COMMAND, report_handler),
            ],
            DONATIONS: [ 
                
                CallbackQueryHandler(ustd_donation, r'^ustd_donation$'),
                CallbackQueryHandler(ton_donation, r'^ton_donation$'),
                CallbackQueryHandler(bitcoin_donation, r'^bitcoin_donation$'),

                MessageHandler(filters.TEXT & ~ filters.COMMAND, donations_handler),
            ],

        },
        fallbacks=[CommandHandler('start', start)],
        # allow_reentry=True,
    ))
    application.run_polling()


if __name__ == "__main__":
    main()

