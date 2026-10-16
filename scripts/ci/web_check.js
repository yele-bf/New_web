#!/usr/bin/env node
/**
 * web_check — contrôle statique du dashboard (aucune dépendance npm).
 *
 *   1. syntaxe de tous les fichiers .js du dépôt (hors node_modules / .git) ;
 *   2. chaque ressource locale référencée par index.html existe bien
 *      (les liens http(s), data: et #ancres sont ignorés, les « ?v=3 » retirés).
 *
 * Sortie : 0 si tout passe, 1 dès qu'un problème est détecté.
 */
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const RACINE = process.cwd();
const IGNORES = new Set(["node_modules", ".git", ".github", "vendor"]);
const problemes = [];
let nbJs = 0;

function fichiersJs(dossier) {
  for (const entree of fs.readdirSync(dossier, { withFileTypes: true })) {
    if (IGNORES.has(entree.name)) continue;
    const chemin = path.join(dossier, entree.name);
    if (entree.isDirectory()) fichiersJs(chemin);
    else if (entree.name.endsWith(".js")) verifierSyntaxe(chemin);
  }
}

function verifierSyntaxe(chemin) {
  nbJs++;
  const relatif = path.relative(RACINE, chemin).replace(/\\/g, "/");
  try {
    new vm.Script(fs.readFileSync(chemin, "utf8"), { filename: relatif });
  } catch (erreur) {
    problemes.push(`${relatif} · syntaxe JS invalide → ${erreur.message}`);
  }
}

function verifierIndex() {
  const index = path.join(RACINE, "index.html");
  if (!fs.existsSync(index)) {
    problemes.push("index.html est absent de la racine du dépôt");
    return;
  }
  const html = fs.readFileSync(index, "utf8");
  const motif = /(?:src|href)\s*=\s*"([^"]+)"/g;
  let nbRefs = 0;
  let trouve;
  while ((trouve = motif.exec(html)) !== null) {
    const brut = trouve[1];
    if (/^(https?:)?\/\//.test(brut) || brut.startsWith("data:") || brut.startsWith("#")) continue;
    const cible = brut.split("?")[0].split("#")[0];
    if (!cible) continue;
    nbRefs++;
    if (!fs.existsSync(path.join(RACINE, cible))) {
      problemes.push(`index.html référence « ${cible} », fichier introuvable`);
    }
  }
  console.log(`web_check · index.html : ${nbRefs} ressource(s) locale(s) vérifiée(s)`);
}

fichiersJs(RACINE);
console.log(`web_check · ${nbJs} fichier(s) JS analysé(s)`);
verifierIndex();

if (problemes.length === 0) {
  console.log("OK - aucun problème détecté.");
  process.exit(0);
}
console.log(`\n${problemes.length} problème(s) :\n`);
for (const p of problemes) console.log(`  x ${p}`);
process.exit(1);
