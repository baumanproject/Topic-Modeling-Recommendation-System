from data_transform import tokenizer, nlp, stopwords_en, data_folder, logger
import fitz


def lemmatizer(text):
    try:
        text_lem = ' '.join([token.lemma_.lower() for token in nlp(text)])
    except:
        logger.warn("Unexpected error during stage lemmitizer")
        return " "
    return text_lem


def preprocessor(text):
    try:
        text_preproc = ' '.join(
            [word for word in tokenizer.tokenize(text) if word not in stopwords_en and len(word) >= 3])
    except:
        logger.warn("Unexpected error during stage preprocessor")
        return " "
    return text_preproc


def cut_reference(text):
    try:
        text_cut = text[:text.index("reference")]
    except:
        logger.warn("Unexpected error during stage preprocessor")
        return " "
    return text_cut


def get_text(pdf_name):
    try:
        doc = fitz.open(data_folder + "/" + pdf_name)
        text = '\n'.join([doc[i].getText() for i, _ in enumerate(doc)])
        # print(text)
    except:
        logger.warn("Error with file : " + pdf_name)
        return ""
    return text
