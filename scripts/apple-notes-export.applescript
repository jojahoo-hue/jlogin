(*
	Export des notes Apple (texte + pieces jointes) vers un dossier de travail.

	Usage :
		osascript scripts/apple-notes-export.applescript <dossier_export> list
		osascript scripts/apple-notes-export.applescript <dossier_export> export [fichier_ids]

	Mode "list"   : ecrit <dossier_export>/index.tsv (id, date modif, date creation, dossier, titre)
	                sans toucher au corps ni aux medias. Rapide, sert a detecter les nouveautes.
	Mode "export" : ecrit un sous-dossier par note dans <dossier_export>/notes/ :
	                  meta.tsv    metadonnees (une ligne cle<TAB>valeur)
	                  body.html   corps de la note au format HTML
	                  media/      pieces jointes sauvegardees telles quelles
	                Si <fichier_ids> est fourni, seules les notes dont l'id y figure
	                (une par ligne) sont exportees.

	Prerequis : Terminal (ou Claude Code) autorise dans
	  Reglages Systeme > Confidentialite et securite > Automatisation > Notes
*)

on run argv
	if (count of argv) < 2 then
		return "ERREUR: usage = <dossier_export> <list|export> [fichier_ids]"
	end if

	set exportDir to item 1 of argv
	set runMode to item 2 of argv
	set wantedIds to {}
	set filterIds to false

	if (count of argv) > 2 then
		set idsFile to item 3 of argv
		set wantedIds to my readLines(idsFile)
		set filterIds to true
	end if

	my ensureDir(exportDir)

	set indexLines to {}
	set exportedCount to 0
	set skippedLocked to 0
	set mediaCount to 0

	tell application "Notes"
		set allNotes to every note
	end tell

	repeat with theNote in allNotes
		set noteId to ""
		set noteName to ""
		set noteFolder to ""
		set isLocked to false
		set createdIso to ""
		set modifiedIso to ""

		try
			tell application "Notes"
				set noteId to (id of theNote) as text
				set noteName to (name of theNote) as text
				set createdIso to my isoDate(creation date of theNote)
				set modifiedIso to my isoDate(modification date of theNote)
				try
					set noteFolder to (name of container of theNote) as text
				on error
					set noteFolder to "Notes"
				end try
				try
					set isLocked to (password protected of theNote)
				on error
					set isLocked to false
				end try
			end tell
		on error errMsg
			log "Note illisible, ignoree : " & errMsg
		end try

		if noteId is not "" then
			set safeName to my oneLine(noteName)
			set end of indexLines to noteId & tab & modifiedIso & tab & createdIso & tab & my oneLine(noteFolder) & tab & safeName & tab & (isLocked as text)

			set mustExport to (runMode is "export")
			if mustExport and filterIds then
				set mustExport to (wantedIds contains noteId)
			end if

			if mustExport then
				if isLocked then
					set skippedLocked to skippedLocked + 1
				else
					set noteDir to exportDir & "/notes/" & my slug(noteId)
					my ensureDir(noteDir)
					my ensureDir(noteDir & "/media")

					set noteBody to ""
					try
						tell application "Notes" to set noteBody to (body of theNote) as text
					end try

					my writeUtf8(noteBody, noteDir & "/body.html")

					set savedMedia to my saveAttachments(theNote, noteDir & "/media")
					set mediaCount to mediaCount + savedMedia

					set metaText to "id" & tab & noteId & linefeed
					set metaText to metaText & "title" & tab & safeName & linefeed
					set metaText to metaText & "folder" & tab & my oneLine(noteFolder) & linefeed
					set metaText to metaText & "created" & tab & createdIso & linefeed
					set metaText to metaText & "modified" & tab & modifiedIso & linefeed
					set metaText to metaText & "media_count" & tab & (savedMedia as text) & linefeed
					my writeUtf8(metaText, noteDir & "/meta.tsv")

					set exportedCount to exportedCount + 1
				end if
			end if
		end if
	end repeat

	my writeUtf8(my joinLines(indexLines), exportDir & "/index.tsv")

	return "OK" & tab & (count of indexLines) & tab & exportedCount & tab & mediaCount & tab & skippedLocked
end run

(* Sauvegarde les pieces jointes d'une note, renvoie le nombre de fichiers ecrits. *)
on saveAttachments(theNote, mediaDir)
	set savedCount to 0
	set attList to {}
	try
		tell application "Notes" to set attList to attachments of theNote
	on error
		return 0
	end try

	set attIndex to 0
	repeat with theAtt in attList
		set attIndex to attIndex + 1
		set attName to ""
		try
			tell application "Notes" to set attName to (name of theAtt) as text
		on error
			set attName to ""
		end try
		if attName is "" or attName is "missing value" then
			set attName to "piece-jointe-" & attIndex
		end if

		set fileName to (my zeroPad(attIndex, 3)) & "-" & my sanitizeFileName(attName)
		set destPath to mediaDir & "/" & fileName

		try
			tell application "Notes" to save theAtt in (POSIX file destPath)
			set savedCount to savedCount + 1
		on error errMsg
			log "Piece jointe non sauvegardee (" & attName & ") : " & errMsg
		end try
	end repeat

	return savedCount
end saveAttachments

on isoDate(d)
	if d is missing value then return ""
	set y to year of d
	set m to (month of d) as integer
	set dd to day of d
	set hh to hours of d
	set mm to minutes of d
	set ss to seconds of d
	return (y as text) & "-" & my zeroPad(m, 2) & "-" & my zeroPad(dd, 2) & "T" & my zeroPad(hh, 2) & ":" & my zeroPad(mm, 2) & ":" & my zeroPad(ss, 2)
end isoDate

on zeroPad(n, width)
	set s to n as text
	repeat while (length of s) < width
		set s to "0" & s
	end repeat
	return s
end zeroPad

(* Remplace retours a la ligne et tabulations pour garder une valeur sur une seule ligne TSV. *)
on oneLine(t)
	set t to my replaceText(t, return, " ")
	set t to my replaceText(t, linefeed, " ")
	set t to my replaceText(t, tab, " ")
	return t
end oneLine

on replaceText(theText, searchStr, replaceStr)
	set savedDelims to AppleScript's text item delimiters
	set AppleScript's text item delimiters to searchStr
	set parts to text items of theText
	set AppleScript's text item delimiters to replaceStr
	set outText to parts as text
	set AppleScript's text item delimiters to savedDelims
	return outText
end replaceText

(* Id Core Data -> nom de dossier utilisable. *)
on slug(t)
	set outText to ""
	repeat with c in (characters of t)
		set ch to c as text
		if ch is in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-" then
			set outText to outText & ch
		else
			set outText to outText & "-"
		end if
	end repeat
	if (length of outText) > 80 then set outText to text -80 thru -1 of outText
	return outText
end slug

on sanitizeFileName(t)
	set t to my replaceText(t, "/", "-")
	set t to my replaceText(t, ":", "-")
	set t to my oneLine(t)
	if (length of t) > 90 then set t to text 1 thru 90 of t
	return t
end sanitizeFileName

on joinLines(theList)
	set savedDelims to AppleScript's text item delimiters
	set AppleScript's text item delimiters to linefeed
	set outText to theList as text
	set AppleScript's text item delimiters to savedDelims
	return outText
end joinLines

on readLines(posixPath)
	try
		set rawText to do shell script "cat " & quoted form of posixPath
	on error
		return {}
	end try
	set savedDelims to AppleScript's text item delimiters
	set AppleScript's text item delimiters to linefeed
	set theLines to text items of rawText
	set AppleScript's text item delimiters to savedDelims
	set cleanLines to {}
	repeat with l in theLines
		set lt to (l as text)
		if lt is not "" then set end of cleanLines to lt
	end repeat
	return cleanLines
end readLines

on ensureDir(posixPath)
	do shell script "mkdir -p " & quoted form of posixPath
end ensureDir

on writeUtf8(theText, posixPath)
	set fileRef to open for access (POSIX file posixPath) with write permission
	try
		set eof fileRef to 0
		write theText to fileRef as «class utf8»
		close access fileRef
	on error errMsg
		try
			close access fileRef
		end try
		error errMsg
	end try
end writeUtf8
