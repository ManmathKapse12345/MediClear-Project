import type { IdentifyStatus, Lang } from './types'

export const LANGS: { code: Lang; label: string }[] = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी' },
  { code: 'mr', label: 'मराठी' },
]

const en = {
  tabScan: 'Find medicine',
  tabExplain: 'About it',
  tabAsk: 'Ask',
  tabMine: 'My medicines',
  language: 'Language',
  disclaimer:
    'MediClear explains medicines. It does not replace your doctor or pharmacist. ' +
    'Always follow their instructions. Do not start, stop or change a medicine without asking them.',
  loading: 'Please wait…',
  comingSoon: 'This part is coming soon.',

  // Scan screen
  scanTitle: 'Find your medicine',
  searchLabel: 'Type the medicine name from the strip',
  searchButton: 'Search',
  or: 'or',
  photoButton: '📷 Take a photo of the strip',
  contains: 'This medicine contains:',
  explain: 'Explain',
  save: 'Save to my medicines',
  saved: 'Saved ✓',
  unverified: 'We could not confirm:',
  status: {
    unreadable: 'We could not read the photo. Take it again in good light, showing the name on the strip.',
    low_confidence: 'We are not sure which medicine this is. Please type its name instead.',
    not_in_db: 'This medicine is not in our list. Please ask your pharmacist.',
    error: 'Something went wrong. Please try again in a little while.',
  } as Record<Exclude<IdentifyStatus, 'ok'>, string>,
}

// Every language must have exactly the same keys as English.
export type Strings = typeof en

const hi: Strings = {
  tabScan: 'दवा खोजें',
  tabExplain: 'जानकारी',
  tabAsk: 'सवाल पूछें',
  tabMine: 'मेरी दवाएँ',
  language: 'भाषा',
  disclaimer:
    'MediClear दवाओं के बारे में समझाता है। यह आपके डॉक्टर या फ़ार्मासिस्ट की जगह नहीं लेता। ' +
    'हमेशा उनकी सलाह मानें। उनसे पूछे बिना कोई दवा शुरू, बंद या बदलें नहीं।',
  loading: 'कृपया रुकें…',
  comingSoon: 'यह हिस्सा जल्द आएगा।',

  scanTitle: 'अपनी दवा खोजें',
  searchLabel: 'पत्ते पर लिखा दवा का नाम लिखें',
  searchButton: 'खोजें',
  or: 'या',
  photoButton: '📷 पत्ते की फ़ोटो लें',
  contains: 'इस दवा में है:',
  explain: 'समझाएँ',
  save: 'मेरी दवाओं में जोड़ें',
  saved: 'जोड़ दी गई ✓',
  unverified: 'इनकी पुष्टि नहीं हो सकी:',
  status: {
    unreadable: 'फ़ोटो साफ़ नहीं पढ़ी जा सकी। अच्छी रोशनी में, पत्ते पर लिखे नाम की फ़ोटो फिर से लें।',
    low_confidence: 'हमें पक्का पता नहीं चला कि यह कौन-सी दवा है। कृपया दवा का नाम लिखकर खोजें।',
    not_in_db: 'यह दवा हमारी सूची में नहीं है। कृपया अपने फ़ार्मासिस्ट से पूछें।',
    error: 'अभी कुछ गड़बड़ हो गई। कृपया थोड़ी देर बाद फिर कोशिश करें।',
  },
}

const mr: Strings = {
  tabScan: 'औषध शोधा',
  tabExplain: 'माहिती',
  tabAsk: 'प्रश्न विचारा',
  tabMine: 'माझी औषधे',
  language: 'भाषा',
  disclaimer:
    'MediClear औषधांबद्दल समजावून सांगते. हे तुमच्या डॉक्टर किंवा फार्मासिस्टची जागा घेत नाही. ' +
    'नेहमी त्यांचा सल्ला पाळा. त्यांना विचारल्याशिवाय कोणतेही औषध सुरू करू नका, बंद करू नका किंवा बदलू नका.',
  loading: 'कृपया थांबा…',
  comingSoon: 'हा भाग लवकरच येईल.',

  scanTitle: 'तुमचे औषध शोधा',
  searchLabel: 'स्ट्रिपवर लिहिलेले औषधाचे नाव लिहा',
  searchButton: 'शोधा',
  or: 'किंवा',
  photoButton: '📷 स्ट्रिपचा फोटो काढा',
  contains: 'या औषधात आहे:',
  explain: 'समजावून सांगा',
  save: 'माझ्या औषधांमध्ये जोडा',
  saved: 'जोडले ✓',
  unverified: 'यांची खात्री होऊ शकली नाही:',
  status: {
    unreadable: 'फोटो नीट वाचता आला नाही. चांगल्या प्रकाशात, स्ट्रिपवरील नावाचा फोटो पुन्हा काढा.',
    low_confidence: 'हे कोणते औषध आहे याची आम्हाला खात्री झाली नाही. कृपया औषधाचे नाव लिहून शोधा.',
    not_in_db: 'हे औषध आमच्या यादीत नाही. कृपया तुमच्या फार्मासिस्टला विचारा.',
    error: 'आत्ता काहीतरी चूक झाली. कृपया थोड्या वेळाने पुन्हा प्रयत्न करा.',
  },
}

const ALL: Record<Lang, Strings> = { en, hi, mr }

export function getStrings(lang: Lang): Strings {
  return ALL[lang]
}