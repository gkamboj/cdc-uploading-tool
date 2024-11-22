import importlib

import langcodes
import translate


def terryin_translate(text, source_language, destination_language):
    src, dest = get_iso_code_for_langauge(source_language), get_iso_code_for_langauge(destination_language)
    if dest:
        if src:
            translator = translate.Translator(from_lang=src, to_lang=dest)
        else:
            translator = translate.Translator(to_lang=dest)
        translated_text = translator.translate(text)
    else:
        translated_text = 'No translation available as destination languages is invalid'
    print(f'Translation done by Terryin library for {text} from {src} to {dest}: {translated_text}')
    return translated_text


def ai_translate(text, source_language, destination_language, service_name):
    src, dest = get_iso_code_for_langauge(source_language), get_iso_code_for_langauge(destination_language)
    var = ''
    if src:
        var = f'from {src} '
    if dest:
        system_prompt = 'You are a language translator'
        prompt = get_translate_prompt(dest, text, var)
        service_module = importlib.import_module(service_name)
        response = service_module.get_prompt_response(prompt, system_prompt)
        translated_text = response.choices[0].message.content
    else:
        translated_text = 'No translation available as destination languages is invalid'
    print(f'''
        Translation done by {service_name} for
            {text} 
        from {src} to {dest}:
            {translated_text}
    ''')
    return translated_text


def get_translate_prompt(dest, text, var):
    prompt = f'''
            Translate the following text {var} to {dest}.
            {text}
            If the text is HTML content, don't change HTML tags. Please provide the translation in {dest}.\
            Return only translated text, no extra information.
        '''
    return prompt


def get_iso_code_for_langauge(language):
    if language:
        try:
            langcode = langcodes.Language.get(language)
        except langcodes.tag_parser.LanguageTagError:
            try:
                langcode = langcodes.find(language.lower())
            except langcodes.tag_parser.LanguageTagError:
                langcode = None
    else:
        langcode = None
    return langcode
