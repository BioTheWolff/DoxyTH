# DoxyTH Changelog
Here are referenced all changes for the updates of DoxyTH

## v1 (Major One)

### v1.1 (Translations update)
This update is focused on allowing the users to have a full translated Doxygen interface
with no issues or errors of any kind.
The readme also got a new section, Troubleshoot, for any referenced problems that might still occur.

* Feature: Adapted Doxygen language to language code of the directory
* Feature: The README got updated with the Pre-requisites and the Troubleshoot sections
* Feature: You can now create your own HTML layout for the languages selection file
* Feature: You can now customise the output directory by using a new command line parameter
* Fix: The lines stripping by adding a safe mode (converts the string to ASCII) 
[fixes #1](https://github.com/BioTheWolff/DoxyTH/issues/1)
* Fix: Removed the auto-optimisation for Java (and Python)
* Fix: The Latin Supplement characters are now replaced by their HTML character version, which should fix the problem
of "question mark block"s appearing.