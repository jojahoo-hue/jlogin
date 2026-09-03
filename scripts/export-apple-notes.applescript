-- Exporte toutes les notes Apple en fichiers Markdown, un sous-dossier par
-- dossier Apple Notes, prêts à être migrés vers Notion.
--
-- Utilisation (sur le Mac), avec un chemin absolu :
--   osascript scripts/export-apple-notes.applescript ~/Documents/jlogin/context/import/apple-notes
--
-- Sans argument, l'export va dans ~/apple-notes-export.
--
-- Au premier lancement, macOS demande l'autorisation de piloter Notes.
-- Si le script échoue avec une erreur -1743, autoriser le Terminal dans
-- Réglages Système > Confidentialité et sécurité > Automatisation > Notes.

on run argv
	if (count of argv) > 0 then
		set destination to item 1 of argv
	else
		set destination to (POSIX path of (path to home folder)) & "apple-notes-export"
	end if

	-- osascript ignore le dossier courant du terminal : un chemin absolu est exigé
	if destination starts with "~/" then
		set destination to (POSIX path of (path to home folder)) & text 3 thru -1 of destination
	else if destination is "~" then
		set destination to POSIX path of (path to home folder)
	end if
	if destination does not start with "/" then
		error "Chemin relatif refusé. Passer un chemin absolu, par exemple : ~/Documents/jlogin/context/import/apple-notes"
	end if
	if destination ends with "/" then
		set destination to text 1 thru -2 of destination
	end if
	do shell script "mkdir -p " & quoted form of destination

	set exportedCount to 0
	set skippedCount to 0
	set usedPaths to {}

	tell application "Notes"
		repeat with theFolder in folders
			set folderName to name of theFolder as text
			if folderName is not "Recently Deleted" and folderName is not "Suppressions récentes" then
				set folderPath to destination & "/" & my sanitize(folderName)
				do shell script "mkdir -p " & quoted form of folderPath
				repeat with theNote in notes of theFolder
					try
						set noteTitle to name of theNote as text
						set noteText to plaintext of theNote as text
						set baseName to my sanitize(noteTitle)
						if baseName is "" then set baseName to "note"
						set filePath to my uniquePath(folderPath, baseName, usedPaths)
						set end of usedPaths to filePath
						my writeUtf8(filePath, noteText)
						set exportedCount to exportedCount + 1
					on error
						-- Une note illisible ne doit pas interrompre tout l'export
						set skippedCount to skippedCount + 1
					end try
				end repeat
			end if
		end repeat
	end tell

	return "Export terminé : " & exportedCount & " note(s) vers " & destination & ", " & skippedCount & " ignorée(s)."
end run


-- Rend un nom de note utilisable comme nom de fichier
on sanitize(theText)
	set forbidden to {"/", ":", "\"", "*", "?", "<", ">", "|", "\\", return, linefeed, tab}
	set cleaned to theText as text
	repeat with badChar in forbidden
		set AppleScript's text item delimiters to (badChar as text)
		set parts to text items of cleaned
		set AppleScript's text item delimiters to "-"
		set cleaned to parts as text
	end repeat
	set AppleScript's text item delimiters to ""

	-- Les fichiers commençant par un point sont ignorés par le script de migration
	if cleaned starts with "." then set cleaned to "note " & cleaned
	if (count of characters of cleaned) > 80 then set cleaned to text 1 thru 80 of cleaned
	return cleaned
end sanitize


-- Evite d'écraser deux notes portant le même titre
on uniquePath(folderPath, baseName, usedPaths)
	set candidate to folderPath & "/" & baseName & ".md"
	set suffix to 2
	repeat while usedPaths contains candidate
		set candidate to folderPath & "/" & baseName & " " & suffix & ".md"
		set suffix to suffix + 1
	end repeat
	return candidate
end uniquePath


-- Ecrit le texte en UTF-8, accents et emojis compris
on writeUtf8(filePath, theText)
	set fileRef to open for access (POSIX file filePath) with write permission
	try
		set eof of fileRef to 0
		write theText to fileRef as «class utf8»
	on error errMsg number errNum
		close access fileRef
		error errMsg number errNum
	end try
	close access fileRef
end writeUtf8
