if($args.length -ne 2) {
	echo "Wrong arguments. Usage:"
    echo "    make_env.PS1 venv_name requirements_file"
    echo "Example:"
    echo "    make_env.PS1 'venv' 'requirements.txt'"
	exit 1
}

$VENV_NAME=$args[0]
$REQ_FILE=$args[1]

if( -not (Test-Path -Path "$VENV_NAME") ){
	python.exe -m venv "$VENV_NAME"
	echo "*" > "$VENV_NAME/.gitignore"
	& "$VENV_NAME/Scripts/python.exe" -m pip install --upgrade pip
	& "$VENV_NAME/Scripts/pip.exe" install -r "$REQ_FILE"
	& "$VENV_NAME/Scripts/pip.exe" freeze > "$VENV_NAME"/requirements.txt
}
