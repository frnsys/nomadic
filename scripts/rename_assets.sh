# If you need to rename all your assets folders and update references to them, you can use this script.
# Execute this in the root of your notes directory.

NEW_NAME=example

# Rename all assets directories.
find . -depth -name "assets" -execdir sh -c 'mv {} $(echo {} | sed "s/assets/${NEW_NAME}/")' \;

# Update all references.
ag -l "assets" "." | while read line
do
    echo "$line"
    sed -i '' 's/assets/$NEW_NAME/g' "$line"
done

