#!/bin/sh
i18ndude rebuild-pot --pot "locales/fhnwoffice2plone" --create fhnwoffice2plone .
i18ndude sync --pot "locales/fhnwoffice2plone.pot" \
    "locales/de/LC_MESSAGES/fhnwoffice2plone.po" \
    "locales/en/LC_MESSAGES/fhnwoffice2plone.po" \
    "locales/fr/LC_MESSAGES/fhnwoffice2plone.po"
