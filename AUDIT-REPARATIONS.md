# Audit et corrections — M3ALEM-PRO

## Corrections incluses
- Titres et descriptions uniques sur les 7 pages indexables.
- URL canonical et métadonnées Open Graph / Twitter sur les 7 pages.
- Données structurées JSON-LD : LocalBusiness sur l’accueil et Service sur les pages de prestations, reliées par un identifiant commun.
- `robots.txt` pointe vers le sitemap ; sitemap XML contient les 7 URL du site.
- Amélioration de l’accessibilité : lien d’évitement, navigation nommée, `main` identifié, focus clavier et libellés des liens de contact.
- Amélioration du responsive et du contraste de la couleur d’accent dans `style.css`.
- Ajout de `favicon.svg` et `404.html`.
- Fichier de vérification Google conservé sans modification.
- Téléphone confirmé et mention « Plus de 10 ans d’expérience » conservés.

## Tests statiques effectués
- Analyse des 8 pages HTML : titre unique, un H1, un main et structure parsable.
- Parsing JSON-LD sur les 7 pages indexables.
- Vérification des liens locaux et des fragments internes.
- Parsing XML du sitemap et vérification des 7 URL uniques.
- Vérification de la directive Sitemap dans robots.txt.
- Vérification de conservation du fichier Google de validation.

## À vérifier après publication GitHub Pages
- Confirmer dans Settings > Pages que la source est `main` et `/ (root)`.
- Confirmer que `https://samani12.github.io/m3alem-pro-site/` répond publiquement.
- Tester les liens `tel:` et WhatsApp sur un téléphone.
- Tester le sitemap et la propriété Search Console en ligne.
- Confirmer les quartiers réellement desservis.
- Ajouter une vraie image de partage Open Graph (1200×630) quand une image de marque est fournie ; aucune image fictive n’a été ajoutée.
- Ne pas publier d’adresse, horaires, prix ou avis structurés non vérifiés.

## Limites
Cette archive ne pousse aucun changement vers GitHub. Les tests effectués sont statiques et locaux ; l’accès public au site n’a pas pu être confirmé depuis l’outil de consultation.
