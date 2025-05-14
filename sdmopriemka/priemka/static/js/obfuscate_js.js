const JavaScriptObfuscator = require('javascript-obfuscator');
const fs = require('fs');

const inputJs = fs.readFileSync('static/js/priemka_lc.js', 'utf8');

const obfuscationResult = JavaScriptObfuscator.obfuscate(inputJs, {
    compact: true,
    controlFlowFlattening: true,
    deadCodeInjection: true,
    renameGlobals: true,
    stringArray: true,
    stringArrayEncoding: ['base64'],
    stringArrayThreshold: 0.75
});

fs.writeFileSync('static/js/priemka_lc_appointments_obfuscated.js', obfuscationResult.getObfuscatedCode());