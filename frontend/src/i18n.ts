import type { AlertLevel, IdentifyStatus, Lang } from './types'

export const LANGS: { code: Lang; label: string }[] = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिंदी" },
  { code: "mr", label: "मराठी" },
];

const en = {
  tabScan: "Find medicine",
  tabExplain: "About it",
  tabAsk: "Ask",
  tabMine: "My medicines",
  language: "Language",
  disclaimer:
    "MediClear explains medicines. It does not replace your doctor or pharmacist. " +
    "Always follow their instructions. Do not start, stop or change a medicine without asking them.",
  loading: "Please wait…",
  comingSoon: "This part is coming soon.",

  // Scan screen
  scanTitle: "Find your medicine",
  searchLabel: "Type the medicine name from the strip",
  searchButton: "Search",
  or: "or",
  photoButton: "📷 Take a photo of the strip",
  contains: "This medicine contains:",
  explain: "Explain",
  save: "Save to my medicines",
  saved: "Saved ✓",
  unverified: "We could not confirm:",
  status: {
    unreadable:
      "We could not read the photo. Take it again in good light, showing the name on the strip.",
    low_confidence:
      "We are not sure which medicine this is. Please type its name instead.",
    not_in_db: "This medicine is not in our list. Please ask your pharmacist.",
    error: "Something went wrong. Please try again in a little while.",
  } as Record<Exclude<IdentifyStatus, "ok">, string>,
  // Explain screen
  noMedicine: 'First find a medicine, then tap "Explain".',
  listen: "🔊 Listen",
  audioFailed:
    "The voice is not available right now. Please read the text below.",
  translatedNote:
    "This was translated by computer from a trusted English source. If anything is unclear, ask your pharmacist.",
  translationBusy:
    "The translation service is busy. Please try again, or read it in English.",
  readInEnglish: "Read in English",
  tryAgain: "Try again",
  usedFor: "What it is for",
  howItWorks: "How it works",
  howToTake: "How to take it",
  avoid: "Avoid",
  sideEffects: "Common side effects",
  seeDoctorIf: "See a doctor if",
  sources: "Sources",
    // Ask screen
  askTitle: 'Ask a question about your medicine',
  questionLabel: 'Type your question',
  questionPlaceholder: 'For example: Is it OK to take this with food?',
  askAbout: 'My question is about:',
  askButton: 'Ask',
  call112: '📞 Call 112',
    // My medicines screen
  mineTitle: 'My medicines',
  mineEmpty: 'You have not saved any medicines yet.',
  remove: 'Remove',
  confirmRemove: 'Yes, remove',
  cancel: 'Cancel',
  savedOn: 'Saved on:',
  alertsTitle: 'Check before taking these together',
  noAlerts:
    'We found no known problems between your saved medicines. Always tell your doctor about every medicine you take.',
  detailsInEnglish: 'Details (in English):',
  level: {
    warning: 'Warning',
    caution: 'Caution',
    timing: 'Timing',
  } as Record<AlertLevel, string>,
  levelAdvice: {
    warning: 'Do not take these together unless your doctor says so.',
    caution: 'Tell your doctor or pharmacist that you take both.',
    timing: 'These can be taken, but not at the same time.',
  } as Record<AlertLevel, string>,
};

// Every language must have exactly the same keys as English.
export type Strings = typeof en;

const hi: Strings = {
  tabScan: "दवा खोजें",
  tabExplain: "जानकारी",
  tabAsk: "सवाल पूछें",
  tabMine: "मेरी दवाएँ",
  language: "भाषा",
  disclaimer:
    "MediClear दवाओं के बारे में समझाता है। यह आपके डॉक्टर या फ़ार्मासिस्ट की जगह नहीं लेता। " +
    "हमेशा उनकी सलाह मानें। उनसे पूछे बिना कोई दवा शुरू, बंद या बदलें नहीं।",
  loading: "कृपया रुकें…",
  comingSoon: "यह हिस्सा जल्द आएगा।",

  scanTitle: "अपनी दवा खोजें",
  searchLabel: "पत्ते पर लिखा दवा का नाम लिखें",
  searchButton: "खोजें",
  or: "या",
  photoButton: "📷 पत्ते की फ़ोटो लें",
  contains: "इस दवा में है:",
  explain: "समझाएँ",
  save: "मेरी दवाओं में जोड़ें",
  saved: "जोड़ दी गई ✓",
  unverified: "इनकी पुष्टि नहीं हो सकी:",
  status: {
    unreadable:
      "फ़ोटो साफ़ नहीं पढ़ी जा सकी। अच्छी रोशनी में, पत्ते पर लिखे नाम की फ़ोटो फिर से लें।",
    low_confidence:
      "हमें पक्का पता नहीं चला कि यह कौन-सी दवा है। कृपया दवा का नाम लिखकर खोजें।",
    not_in_db:
      "यह दवा हमारी सूची में नहीं है। कृपया अपने फ़ार्मासिस्ट से पूछें।",
    error: "अभी कुछ गड़बड़ हो गई। कृपया थोड़ी देर बाद फिर कोशिश करें।",
  },
  noMedicine: 'पहले दवा खोजें, फिर "समझाएँ" दबाएँ।',
  listen: "🔊 सुनें",
  audioFailed: "अभी आवाज़ उपलब्ध नहीं है। कृपया नीचे लिखा पढ़ें।",
  translatedNote:
    "यह जानकारी भरोसेमंद अंग्रेज़ी स्रोत से कंप्यूटर द्वारा अनुवाद की गई है। कोई शक हो तो अपने फ़ार्मासिस्ट से पूछें।",
  translationBusy:
    "अनुवाद सेवा अभी व्यस्त है। कृपया फिर कोशिश करें, या अंग्रेज़ी में पढ़ें।",
  readInEnglish: "अंग्रेज़ी में पढ़ें",
  tryAgain: "फिर कोशिश करें",
  usedFor: "यह किसलिए है",
  howItWorks: "यह कैसे काम करती है",
  howToTake: "कैसे लें",
  avoid: "इनसे बचें",
  sideEffects: "आम दुष्प्रभाव",
  seeDoctorIf: "डॉक्टर को दिखाएँ अगर",
  sources: "स्रोत",
  askTitle: 'अपनी दवा के बारे में सवाल पूछें',
  questionLabel: 'अपना सवाल लिखें',
  questionPlaceholder: 'जैसे: क्या इसे खाने के साथ लेना ठीक है?',
  askAbout: 'सवाल इस दवा के बारे में है:',
  askButton: 'पूछें',
  call112: '📞 112 पर कॉल करें',
  mineTitle: 'मेरी दवाएँ',
  mineEmpty: 'आपने अभी तक कोई दवा नहीं जोड़ी है।',
  remove: 'हटाएँ',
  confirmRemove: 'हाँ, हटाएँ',
  cancel: 'रद्द करें',
  savedOn: 'जोड़ने की तारीख:',
  alertsTitle: 'इन दवाओं को साथ लेने से पहले ध्यान दें',
  noAlerts:
    'आपकी जोड़ी गई दवाओं के बीच हमें कोई ज्ञात समस्या नहीं मिली। फिर भी अपने डॉक्टर को अपनी सभी दवाओं के बारे में ज़रूर बताएँ।',
  detailsInEnglish: 'पूरी जानकारी (अंग्रेज़ी में):',
  level: {
    warning: 'चेतावनी',
    caution: 'सावधानी',
    timing: 'समय का ध्यान',
  },
  levelAdvice: {
    warning: 'डॉक्टर की सलाह के बिना इन्हें साथ में न लें।',
    caution: 'अपने डॉक्टर या फ़ार्मासिस्ट को बताएँ कि आप दोनों दवाएँ लेते हैं।',
    timing: 'इन्हें ले सकते हैं, लेकिन एक ही समय पर नहीं।',
  },
};

const mr: Strings = {
  tabScan: "औषध शोधा",
  tabExplain: "माहिती",
  tabAsk: "प्रश्न विचारा",
  tabMine: "माझी औषधे",
  language: "भाषा",
  disclaimer:
    "MediClear औषधांबद्दल समजावून सांगते. हे तुमच्या डॉक्टर किंवा फार्मासिस्टची जागा घेत नाही. " +
    "नेहमी त्यांचा सल्ला पाळा. त्यांना विचारल्याशिवाय कोणतेही औषध सुरू करू नका, बंद करू नका किंवा बदलू नका.",
  loading: "कृपया थांबा…",
  comingSoon: "हा भाग लवकरच येईल.",

  scanTitle: "तुमचे औषध शोधा",
  searchLabel: "स्ट्रिपवर लिहिलेले औषधाचे नाव लिहा",
  searchButton: "शोधा",
  or: "किंवा",
  photoButton: "📷 स्ट्रिपचा फोटो काढा",
  contains: "या औषधात आहे:",
  explain: "समजावून सांगा",
  save: "माझ्या औषधांमध्ये जोडा",
  saved: "जोडले ✓",
  unverified: "यांची खात्री होऊ शकली नाही:",
  status: {
    unreadable:
      "फोटो नीट वाचता आला नाही. चांगल्या प्रकाशात, स्ट्रिपवरील नावाचा फोटो पुन्हा काढा.",
    low_confidence:
      "हे कोणते औषध आहे याची आम्हाला खात्री झाली नाही. कृपया औषधाचे नाव लिहून शोधा.",
    not_in_db: "हे औषध आमच्या यादीत नाही. कृपया तुमच्या फार्मासिस्टला विचारा.",
    error: "आत्ता काहीतरी चूक झाली. कृपया थोड्या वेळाने पुन्हा प्रयत्न करा.",
  },
  noMedicine: 'आधी औषध शोधा, मग "समजावून सांगा" दाबा.',
  listen: "🔊 ऐका",
  audioFailed: "आत्ता आवाज उपलब्ध नाही. कृपया खाली लिहिलेले वाचा.",
  translatedNote:
    "ही माहिती विश्वसनीय इंग्रजी स्रोतावरून संगणकाने भाषांतरित केली आहे. काही शंका असल्यास तुमच्या फार्मासिस्टला विचारा.",
  translationBusy:
    "भाषांतर सेवा सध्या व्यस्त आहे. कृपया पुन्हा प्रयत्न करा, किंवा इंग्रजीत वाचा.",
  readInEnglish: "इंग्रजीत वाचा",
  tryAgain: "पुन्हा प्रयत्न करा",
  usedFor: "हे कशासाठी आहे",
  howItWorks: "हे कसे काम करते",
  howToTake: "कसे घ्यावे",
  avoid: "हे टाळा",
  sideEffects: "सामान्य दुष्परिणाम",
  seeDoctorIf: "असे झाल्यास डॉक्टरांना दाखवा",
  sources: "स्रोत",
  askTitle: 'तुमच्या औषधाबद्दल प्रश्न विचारा',
  questionLabel: 'तुमचा प्रश्न लिहा',
  questionPlaceholder: 'उदा: हे जेवणासोबत घेणे ठीक आहे का?',
  askAbout: 'प्रश्न या औषधाबद्दल आहे:',
  askButton: 'विचारा',
  call112: '📞 112 वर कॉल करा',
  mineTitle: 'माझी औषधे',
  mineEmpty: 'तुम्ही अजून कोणतेही औषध जोडलेले नाही.',
  remove: 'काढा',
  confirmRemove: 'होय, काढा',
  cancel: 'रद्द करा',
  savedOn: 'जोडल्याची तारीख:',
  alertsTitle: 'ही औषधे एकत्र घेण्यापूर्वी लक्ष द्या',
  noAlerts:
    'तुमच्या जोडलेल्या औषधांमध्ये आम्हाला कोणतीही ज्ञात समस्या आढळली नाही. तरीही तुम्ही घेत असलेल्या सर्व औषधांबद्दल डॉक्टरांना नक्की सांगा.',
  detailsInEnglish: 'संपूर्ण माहिती (इंग्रजीत):',
  level: {
    warning: 'इशारा',
    caution: 'सावधगिरी',
    timing: 'वेळेकडे लक्ष द्या',
  },
  levelAdvice: {
    warning: 'डॉक्टरांनी सांगितल्याशिवाय ही औषधे एकत्र घेऊ नका.',
    caution: 'तुम्ही दोन्ही औषधे घेता हे तुमच्या डॉक्टर किंवा फार्मासिस्टला सांगा.',
    timing: 'ही औषधे घेता येतात, पण एकाच वेळी नाही.',
  },
};

const ALL: Record<Lang, Strings> = { en, hi, mr };

export function getStrings(lang: Lang): Strings {
  return ALL[lang];
}
