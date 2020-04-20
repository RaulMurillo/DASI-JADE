import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import PeriodicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade


import logging
import os
import dialogflow
import json
import datetime

from google.api_core.exceptions import InvalidArgument
from telegram import ReplyKeyboardMarkup
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

messageAlergia = None
messagePreferencia = None
messageImage = None
messageReceta = None


# class SenderAgent(Agent):

#     class SendBehav(PeriodicBehaviour):
#         async def on_start(self):
#             print("Starting behaviour . . .")

#         async def run(self):
#             logging.debug("SendBehav running")
#             print("SenderAgent running . . .")

#             global messageAlergia
#             global messagePreferencia
#             global messageImage
#             global messageReceta
#             print("Estado de messagePreferencia" + str(messagePreferencia))
#             if(messageAlergia != None):

#                 # "akjncakj1@616.pub")     # Instantiate the message
#                 msg = Message(to="dasi2020cheff@616.pub")
#                 # Alergia o Preferencia
#                 msg.set_metadata("performative", "inform_ref")
#                 # Set the message content
#                 # msg.body = str(messageAlergia)
#                 logging.info(f"[ALERGIAS] {str(messageAlergia)}")
#                 # for k in str(messageAlergia).split(','):
#                 #     msg.body = k + ',-10'
#                 #     await self.send(msg)

#                 msg.body = '8,-10'
#                 await self.send(msg)
#                 messageAlergia = None
#             elif(messagePreferencia != None):

#                 # Instantiate the message
#                 msg = Message(to="dasi2020cheff@616.pub")
#                 # Alergia o Preferencia
#                 msg.set_metadata("performative", "inform_ref")
#                 logging.info(f"[PREFERENCIAS] {str(messagePreferencia)}")
#                 # msg.body = str(messagePreferencia)
#                 msg.body = '20,5'
#                 await self.send(msg)
#                 messagePreferencia = None
#             elif(messageImage != None):

#                 # "akjncakj1@616.pub")
#                 msg = Message(to="dasi2020image@616.pub")
#                 # Start cooking
#                 msg.set_metadata("performative", "request")  # "inform_ref")
#                 msg.body = str(messageImage)
#                 await self.send(msg)
#                 messageImage = None
#             elif(messageReceta != None):

#                 msg = Message(to="akjncakj1@616.pub")
#                 # Start cooking
#                 msg.set_metadata("performative", "inform_ref")
#                 msg.body = str(messageReceta)
#                 await self.send(msg)
#                 messageReceta = None
#             else:
#                 print("Nothing to send")
#                 pass
#             pass
#             # await asyncio.sleep(1)

#     async def setup(self):
#         print("SenderAgent starting . . .")
#         b = self.SendBehav(period=1.0)
#         self.add_behaviour(b)


# class ReceiveAgent(Agent):
#     """Agent for testing
#     Receive message to this agent
#     """
#     class ReceiveAlergia(PeriodicBehaviour):
#         async def on_start(self):
#             print("Starting behaviour . . .")

#         async def run(self):
#             logging.debug("ReceivePref running")
#             t = 100
#             msg = await self.receive(timeout=t)
#             if msg:
#                 logging.info(
#                     "[Alergia] Message received with content: {}".format(msg.body))
#             else:
#                 logging.info(
#                     f"[Alergia] Did not receive any message after {t} seconds")
#                 # self.kill()
#                 return

#     class ReceiveFoto(PeriodicBehaviour):
#         async def on_start(self):
#             print("Starting behaviour . . .")

#         async def run(self):
#             logging.debug("ReceivePref running")
#             t = 10
#             msg = await self.receive(timeout=t)
#             if msg:
#                 logging.info(
#                     "[Foto] Message received with content: {}".format(msg.body))
#             else:
#                 logging.info(
#                     f"[Foto] Did not receive any message after {t} seconds")
#                 # self.kill()
#                 return
#             pass

#     class ReceivePref(PeriodicBehaviour):
#         async def on_start(self):
#             print("Starting behaviour . . .")

#         async def run(self):
#             logging.debug("ReceivePref running")
#             t = 100
#             msg = await self.receive(timeout=t)
#             if msg:
#                 print(
#                     "[Preferences] Message received with content: {}".format(msg.body))
#                 logging.info(
#                     "[Preferences] Message received with content: {}".format(msg.body))
#             else:
#                 print(
#                     "[Preferences] Did not receive any message after {t} seconds")
#                 logging.info(
#                     f"[Preferences] Did not receive any message after {t} seconds")
#                 return
#             pass

#     async def setup(self):
#         print("ReceiveAgent starting . . .")
#         b = self.ReceiveAlergia(period=0.1)
#         c = self.ReceiveFoto(period=0.1)
#         d = self.ReceivePref(period=0.1)
#         t_b = Template()
#         t_b.set_metadata("performative", "inform")
#         t_c = Template()
#         t_c.set_metadata("performative", "inform_ref")
#         t_d = Template()
#         t_d.set_metadata("performative", "request")
#         self.add_behaviour(b, t_b)
#         self.add_behaviour(c, t_c)
#         self.add_behaviour(d, t_d)


## ---------------------------------- START DIALOGFLOW -----------------------------------------##
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# DialogFlow Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'

DIALOGFLOW_PROJECT_ID = 'dasibot-pfrrfb'
DIALOGFLOW_LANGUAGE_CODE = 'es'
SESSION_ID = 'me'


def call2dialogflow(input_text):
    # Init API
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
    text_input = dialogflow.types.TextInput(
        text=input_text, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(
            session=session, query_input=query_input)
    except InvalidArgument:
        raise Exception('Dialogflow request failed')

    r = {
        'fulfillment': response.query_result.fulfillment_text,
        'intent': response.query_result.intent.display_name,
    }
    # and (r['intent']!= 'Default Fallback Intent')
    if (response.query_result.all_required_params_present):
        # There is no need to ask again
        valorFields = None
        if(r['intent'] == "GuardarGusto") or (r['intent'] == "GuardarAlergia"):
            valorFields = "Ingredientes"
        elif(r['intent'] == "GuardarReceta"):
            valorFields = "Receta"
        else:
            # raise ValueError
            return r

        r['fields'] = response.query_result.parameters.fields[valorFields]
    # else:
    #     print(
    #         f'no req.params present - {response.query_result.all_required_params_present}')
    return r


## ---------------------------------- END DIALOGFLOW -------------------------------------------##
## ---------------------------------- START TELEGRAM -------------------------------------------##

# State definitions for Telegram Bot
(SELECTING_ACTION, ADD_RECIPE, ADD_PHOTO,
 ASK_CHEFF, ADD_PREFS) = map(chr, range(5))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Different constants for this example
(START_OVER, RECIPE, INTENT, FULFILLMENT, FIELDS) = map(chr, range(10, 15))


def start(update, context):
    """Select an action: query by recipes/ingredients or add preferences."""
    text = 'Puedo ayudarte a proponerte una receta con los ingredientes que me mandes en una imagen.\n' + \
        'Tambien puedes indicar tus preferencias y alergias.\n' + \
        'Selecciona la opción de que desees y pulsa finalizar cuando hayas terminado\n\n'

    buttons = [['Quiero cocinar algo, pero no se me ocurre nada', 'Quiero preparar una receta concreta'],
               ['Añadir preferencia', 'Añadir alergia'],
               ['Finalizar']]
    keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)

    # If we're starting over we don't need do send a new message
    if not context.user_data.get(START_OVER):
        update.message.reply_text(
            'Hola! Me llamo DASI-Chef Bot pero puedes llamarme Chef Bot.')
    update.message.reply_text(text=text, resize_keyboard=True, reply_markup=keyboard)

    # Clear Dialogflow context
    call2dialogflow('Hola DASI-Chef Bot')

    context.user_data.clear()
    context.user_data[START_OVER] = True
    return SELECTING_ACTION


def display_info(update, context):
    """Show software user manual in GUI"""
    # TODO
    text = 'Información actualmente no disponible :('
    update.message.reply_text(text=text)
    return SELECTING_ACTION


def done(update, context):
    update.message.reply_text('Hasta la próxima!')

    context.user_data.clear()
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def detect_intention(update, context):
    """Detect user's intention from input text."""
    # Use Dialogflow to detect user's intention (use case)
    text = update.message.text
    response = call2dialogflow(text)
    # Store values
    try:
        context.user_data[FULFILLMENT] = response['fulfillment']
        context.user_data[INTENT] = response['intent']

        logging.info(f'INTENT: {context.user_data[INTENT]}')
    except KeyError:
        update.message.reply_text('Error with Dialogflow server')
        exit(1)

    try:
        context.user_data[FIELDS] = response['fields']

        logging.info(f'FIELDS: {context.user_data[FIELDS]}')
    except KeyError:
        logging.debug('No fields in Dialogflow response')

    if context.user_data[INTENT] == 'ConsultarPlatoAElaborar':  # CU01
        return adding_images(update, context)
    elif context.user_data[INTENT] == 'GuardarReceta':  # CU02
        return adding_recipe(update, context)
    elif (context.user_data[INTENT] == 'GuardarGusto') or (context.user_data[INTENT] == 'GuardarAlergia'):  # CU03
        return adding_prefs(update, context)
    # elif context.user_data[INTENT] == 'GuardarAlergia':
    #     return adding_allergies(update, context)
    else:
        # context.user_data[INTENT] == 'Default Fallback Intent'
        update.message.reply_text(context.user_data[FULFILLMENT])
        # context.user_data.clear()
        context.user_data[INTENT] = None

    return SELECTING_ACTION


def adding_images(update, context):
    """Add the images of ingredients."""
    update.message.reply_text(context.user_data[FULFILLMENT])
    info_text = 'Introduce todas las fotos de los ingredientes que tengas.\n' + \
        'Avísame cuando hayas terminado de introducir fotos.\n'
    # 'Procura que aparezca un alimento por imagen.\n' + \
    update.message.reply_text(info_text)

    return ADD_PHOTO


def save_image(update, context):
    """Save the input images."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    currentDT = datetime.datetime.now()

    # TODO: Set un main
    photo_dir = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(photo_dir):
        os.makedirs(photo_dir)
    # try:
    #     os.mkdir(photo_dir, )
    #     print("Directory ", photo_dir, " created")
    # except FileExistsError:
    #     print("Directory ", photo_dir, " already exists")
    photo_name = 'user_photo' + \
        currentDT.strftime("%Y-%m-%d-%H-%M-%S") + '.jpg'
    photo_path = os.path.join(photo_dir, photo_name)
    photo_file.download(photo_path)
    logger.info("Image of %s: %s", user.first_name, photo_name)

    # TODO: Send message to Chat Agent
    # global messageImage
    messageImage = photo_path
    logger.info("messageInfo updated to: %s", messageImage)
    text = "SendImage"

    # TODO: Change by Image agent's response
    update.message.reply_text(f'Uploaded image as {photo_name}!')

    return ADD_PHOTO


def stop_images(update, context):
    update.message.reply_text(
        'Genial! Voy a ver qué puedo hacer con todos estos ingredientes...')

    # TODO: Send message to Chat Agent
    if not context.user_data.get(RECIPE):
        # CU-001
        update.message.reply_text('[CU-001] Obtener recetas')

    else:
        # CU-002
        update.message.reply_text('[CU-002] Obtener ingredientes restantes')

    # TODO: Receive answer from Chat Agent (another state?)

    buttons = [['Sí', 'No']]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)

    update.message.reply_text(text='¿Quieres realizar alguna consulta más?', reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return ASK_CHEFF


def adding_recipe(update, context):
    """Add the recipe you would like to cook."""
    if FIELDS in context.user_data:
        # Recipe already introduced by the user
        return save_recipe(update, context)
    else:
        update.message.reply_text(context.user_data[FULFILLMENT])
        return ADD_RECIPE
    # Unreachable
    return END


def save_recipe(update, context):
    """Save input for recipe and return to next state."""
    # Get recipe, if not introduced previously
    if FIELDS not in context.user_data:
        # Validate with Dialogflow
        response = call2dialogflow(update.message.text)

        try:
            context.user_data[FULFILLMENT] = response['fulfillment']
            # context.user_data[INTENT] = response['intent'] # Should be already set

            # logging.info(context.user_data[INTENT])
        except KeyError:
            update.message.reply_text('Error with Dialogflow server')
            exit(1)

        try:
            context.user_data[FIELDS] = response['fields']
            if len(context.user_data[FIELDS].list_value.values) > 1:
                update.message.reply_text(
                'Por favor, introduce una sola receta, o escribe \'salir\' para volver')
                return ADD_RECIPE
        except KeyError:
            update.message.reply_text(
                'Lo siento, no conozco esa receta.\nPrueba con otra, o escribe \'salir\' para volver')
            return ADD_RECIPE

    # Save recipe to cook
    context.user_data[RECIPE] = context.user_data[FIELDS].list_value.values[0].string_value
    context.user_data[FIELDS] = None
    logging.info(context.user_data[RECIPE])
    return adding_images(update, context)


def adding_prefs(update, context):
    """Add likes or allergies to the system."""
    if FIELDS in context.user_data:
        # Allergies already introduced by the user
        return save_prefs(update, context)

    else:
        update.message.reply_text(context.user_data[FULFILLMENT])
        return ADD_PREFS
    return END  # Unreachable


def save_prefs(update, context):
    """Save detected likes or allergies into system."""
    
    # Fake ingreds list
    INGREDIENTS = ['AJO', 'JUDÍAS', 'PERA', 'LIMÓN', 'TOMATE']
    # Get ingredients, if not introduced previously
    if FIELDS not in context.user_data:
        # Validate with Dialogflow
        response = call2dialogflow(update.message.text)

        try:
            context.user_data[FULFILLMENT] = response['fulfillment']
            # context.user_data[INTENT] = response['intent'] # Should be already set
        except KeyError:
            update.message.reply_text('Error with Dialogflow server')
            exit(1)

        try:
            context.user_data[FIELDS] = response['fields']
        except KeyError:
            update.message.reply_text(
                'Lo siento, no conozco ninguno de esos alimentos')
    # Save ingredients preferences
    if FIELDS in context.user_data:
        update.message.reply_text(context.user_data[FULFILLMENT])

        # Detect all possible ingreds in user message
        unknowns = []
        for i in context.user_data[FIELDS].list_value.values:
            ingredient = i.string_value
            if ingredient not in INGREDIENTS:
                unknowns.append(ingredient)
            else:
                # TODO: send to Chat Agent
                e = INGREDIENTS.index(ingredient)
                # if context.user_data[INTENT] == 'GuardarAlergia'

        if len(unknowns) > 0:
            my_string = ', '.join(unknowns)
            update.message.reply_text(
                f'Lo siento, no conozco estos alimentos: {my_string}.\nPrueba con otros.')
    # Ask for more ingredients or leave
    buttons = [['Sí', 'No']]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)

    prefs_text = 'que no puedas tomar' if context.user_data[
        INTENT] == 'GuardarAlergia' else 'que te guste especialmente'
    
    update.message.reply_text(
        f'¿Hay algún otro alimento {prefs_text}?', reply_markup=keyboard)
    # Next state's FULFILLMENT
    prefs_list = 'alergias' if context.user_data[INTENT] == 'GuardarAlergia' else 'preferencias'
    context.user_data[
        FULFILLMENT] = f'¿Qué más alimentos quieres introducir en tu lista de {prefs_list}?'
    context.user_data[START_OVER] = True
    context.user_data.pop(FIELDS, None)  # Delete fields
    return ADD_PREFS


def telegramBot_main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        "1109746327:AAEfk6ivUvhR23M6z1BBOHvKKb5pHHwSGlQ", use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SELECTING_ACTION: [
                CommandHandler('info', display_info),
                # MessageHandler(Filters.regex('^CU01$'), adding_images),
                # MessageHandler(Filters.regex('^CU02$'), adding_recipe),
                # MessageHandler(Filters.regex('^CU03A$'), adding_prefs),
                # MessageHandler(Filters.regex('^CU03B$'), adding_prefs),
                MessageHandler(Filters.text, detect_intention),
            ],
            ADD_RECIPE: [
                MessageHandler(Filters.regex('^salir$'), start),
                MessageHandler(Filters.text, save_recipe),
            ],
            ADD_PHOTO: [
                MessageHandler(Filters.text, stop_images),
                MessageHandler(Filters.photo, save_image),
            ],
            ASK_CHEFF: [
                MessageHandler(Filters.regex(r'^[Ss][IiÍí]$'), start),
                MessageHandler(Filters.regex(r'^[Nn][Oo]$'), done),
            ],
            ADD_PREFS: [
                MessageHandler(Filters.regex(r'^[Ss][IiÍí]$'), adding_prefs),
                MessageHandler(Filters.regex(r'^[Nn][Oo]$'), start),
                MessageHandler(Filters.text, save_prefs),
            ],
        },

        fallbacks=[
            CommandHandler('exit', done),
            MessageHandler(Filters.regex('^Finalizar$'), done),
        ]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
## ---------------------------------- END TELEGRAM -----------------------------------------------##


if __name__ == "__main__":

    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO)

    # senderAgent = SenderAgent("akjncakj@616.pub", "123456")
    # future = senderAgent.start()
    # future.result()

    # receiver = ReceiveAgent("akjncakj1@616.pub", "123456")
    # receiver.start()

    telegramBot_main()
    print("Wait until user interrupts with ctrl+C")
    # while True:
    #     try:
    #         time.sleep(1)
    #     except KeyboardInterrupt:
    #         break
    # senderAgent.stop()
    # receiver.stop()
    # logging.debug("[INFO] Agents finished")
    # quit_spade()
