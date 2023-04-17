#!/bin/sh
HERE=$(dirname $0)
source "${HERE}/prettify.sh"

info 'Waiting for redis to start...'
${PROJECT_DIR}/scripts/wait-for.sh redis:6379 -t 60 -- echo 'Redis is up'

info "Generating .pot file for translations..."
pot_file="${PROJECT_DIR}/translations/prompts.pot"
pot_backup_file="${PROJECT_DIR}/translations/prompts.pot.back"
touch "${pot_file}"
cp "${pot_file}" "${pot_backup_file}"

# Generate .pot file
xgettext -k_ -o "${pot_file}" ${PROJECT_DIR}/src/prompts/*.py

# Compare the .pot files excluding the "POT-Creation-Date:" line
POT_CHANGED=$(diff <(grep -v "POT-Creation-Date:" "${pot_file}") <(grep -v "POT-Creation-Date:" "${pot_backup_file}"))

# Remove the backup file
rm "${pot_backup_file}"

# Create or update .po files for each language and compile them to .mo files
for lang in $(echo "$LANGUAGES" | tr ',' ' '); do
    po_file="${PROJECT_DIR}/translations/${lang}/${lang}.po"
    mo_file="${PROJECT_DIR}/translations/${lang}/LC_MESSAGES/prompts.mo"
    mkdir -p "$(dirname "${mo_file}")"

    if [ ! -f "${po_file}" ]; then
        info "Creating .po file for ${lang}..."
        msginit -i "${pot_file}" -o "${po_file}" --locale="${lang}"
    elif [ -n "${POT_CHANGED}" ]; then
        info "Updating .po file for ${lang}..."
        msgmerge -U "${po_file}" "${pot_file}"
    fi

    info "Compiling .po file to .mo file for ${lang}..."
    msgfmt "${po_file}" -o "${mo_file}"
done

echo "yeet 6"
info "Starting Python application..."
python ${PROJECT_DIR}/src/app.py
