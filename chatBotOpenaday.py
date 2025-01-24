import streamlit as st
from PIL import Image
from openai import OpenAI  # Importa la classe OpenAI dalla libreria openai
import requests
from io import BytesIO
import os

# Chiedi all'utente di inserire la chiave API di OpenAI
openai_api_key = st.text_input("Inserisci la tua OpenAI API Key:", type="password")

if not openai_api_key:
    st.warning("Per favore, inserisci la tua OpenAI API Key per procedere.")
    st.stop()  # Ferma l'esecuzione dell'app fino a quando non viene inserita la chiave


# Crea un'istanza del client OpenAI
client = OpenAI(
    api_key=openai_api_key
)


def generate_dalle_image(prompt):
    """Genera un'immagine utilizzando il modello DALL·E migliorato."""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,  # Numero di immagini da generare
            size="1024x1024",  # Dimensioni massime supportate per immagini di alta qualità
        )
        image_url = response.data[0].url  # URL dell'immagine generata
        return image_url
    except Exception as e:
        st.error(f"Errore durante la generazione dell'immagine: {e}")
        return None
    
    
def generate_chatgpt_response(prompt):
    """Ottiene una risposta da ChatGPT."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Assicurati di utilizzare il modello corretto
            messages=st.session_state.conversation_memory,
            max_tokens=150,  # Limita la lunghezza della risposta per gestire i costi
            temperature=0.7,  # Controlla la creatività della risposta
        )
        response_content = response.choices[0].message.content
        # Aggiungi la risposta del bot alla memoria
        st.session_state.conversation_memory.append({"role": "assistant", "content": response_content})
        return response_content
    except Exception as e:
        st.error(f"Errore durante la generazione della risposta: {e}")
        return "Mi dispiace, non posso rispondere in questo momento."

# Funzione per autenticare l'utente
def authenticate(password):
    return password == "openday2025"

# Inizializza lo stato di autenticazione, la lista delle immagini e la memoria della conversazione se non già fatto
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

if 'conversation_memory' not in st.session_state:
    st.session_state.conversation_memory = [
        {
            "role": "system",
            "content": "Sei un assistente virtuale amichevole che interagisce con i ragazzi durante l'openday dell'Istituto Superiore Antonio Segni di Ozieri. Siamo all'ra di Informatica, con il prof Ledda, che ha deciso di fare un contest di immagini fra vari gruppi della classe. Oggi sono presenti sia i ragazzi dell'istituto che quelli delle scuole medie. Il tuo compito è aiutare a generare prompt per immagini, interagendo in modo amichevole e coinvolgente. Puoi fare domande come: 'Tu sei un ragazzo delle medie oppure dell'Istituto Antonio Segni?' per capire meglio chi hai davanti. Quando aiuti i ragazzi a generare i prompt, se ti chiedono tante domande, puoi fare battute simpatiche con i ragazzi tipo: forse vi sto aiutando un po' troppo, prof Ledda potrebbe non essere d accordo! Adatta il linguaggio al livello di chi ti parla, ma senza mai usare emoji. Prima di fornire un prompt, fai domande per capire bene come definire il prompt. Ogni volta che proponi un prompt, cerca di stimolarli ad aggiungere ulteriori dettagli"
        }
    ]


# Configura la barra laterale con il logo
with st.sidebar:
    try:
        logo = Image.open("logo.jpg")
        st.image(logo, use_column_width=True)
    except FileNotFoundError:
        st.warning("Logo non trovato. Assicurati che 'logo.jpg' sia nella stessa directory dello script.")
    
    st.markdown("---")  # Separatore
    st.write("**Openday 2025**")
    st.write("Istituto Antonio Segni Ozieri")
    st.markdown("---")
    st.write("### Navigazione")
    # Puoi aggiungere ulteriori elementi alla sidebar se necessario

# Se non autenticato, mostra il campo per la password
if not st.session_state.authenticated:
    st.title("Accesso Riservato")
    password = st.text_input("Inserisci la password per accedere:", type="password")
    if st.button("Accedi"):
        if authenticate(password):
            st.session_state.authenticated = True
            st.success("Autenticazione riuscita!")
        else:
            st.error("Password errata. Riprova.")
else:
    # Carica e mostra l'immagine 'locandina2.jpg' in alto
    try:
        locandina = Image.open("locandina2.jpg")
        st.image(locandina, use_column_width=True)
    except FileNotFoundError:
        st.warning("Immagine 'locandina2.jpg' non trovata. Assicurati che il file sia nella stessa directory dello script.")
    
    # Configura l'interfaccia di Streamlit
    st.title("Openday 2025 - Istituto Antonio Segni Ozieri")
    st.write("Inserisci un prompt per generare un'immagine usando il modello DALL·E.")
    
    # Input dell'utente per generare immagini
    prompt = st.text_input("Prompt per l'immagine:", placeholder="Descrivi l'immagine da generare")
    
    if st.button("Genera Immagine"):
        if prompt:
            st.write(f"Generando un'immagine per il prompt: **{prompt}**")
            image_url = generate_dalle_image(prompt)
            if image_url:
                # Aggiungi l'URL dell'immagine alla lista nello session_state
                st.session_state.generated_images.append({
                    'prompt': prompt,
                    'url': image_url
                })
                st.success("Immagine generata con successo!")
            else:
                st.error("Non è stato possibile generare l'immagine. Riprova.")
        else:
            st.warning("Per favore, inserisci un prompt valido.")
    
    st.markdown("---")
    
    # Sezione per le immagini generate
    st.header("Immagini Generate")
    
    # Visualizza tutte le immagini generate
    if st.session_state.generated_images:
        for idx, img in enumerate(st.session_state.generated_images, start=1):
            st.subheader(f"Immagine {idx}: {img['prompt']}")
            st.image(img['url'], use_column_width=True)
    
            # Scarica l'immagine
            try:
                response = requests.get(img['url'])
                response.raise_for_status()
                pil_image = Image.open(BytesIO(response.content))
                buffered = BytesIO()
                pil_image.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()
    
                st.download_button(
                    label="Scarica Immagine",
                    data=img_bytes,
                    file_name=f"dalle_image_{idx}.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Errore durante il download dell'immagine {idx}: {e}")
    else:
        st.info("Nessuna immagine generata finora.")
    
    st.markdown("---")
    
    # Sezione Chatbot
    st.header("Chat con il nostro Assistente Virtuale")
    chat_input = st.text_input("Tu:", placeholder="Scrivi un messaggio al chatbot")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if st.button("Invia", key="send_chat"):
        if chat_input:
            # Aggiungi il messaggio dell'utente alla memoria della conversazione
            st.session_state.conversation_memory.append({"role": "user", "content": chat_input})
            st.session_state.chat_history.append({"role": "user", "content": chat_input})
            
            # Ottieni la risposta dal chatbot
            response = generate_chatgpt_response(chat_input)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            st.warning("Per favore, inserisci un messaggio.")
    
    # Mostra la cronologia della chat
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            if chat['role'] == 'user':
                st.markdown(f"**Tu:** {chat['content']}")
            elif chat['role'] == 'assistant':
                st.markdown(f"**Assistente:** {chat['content']}")

