Soundvault
==========
A sound preset/program collection format.

Since the programs in DSE are unique for each track, this lib introduces the concept of the "sound vault".
This package helps collecting all programs from all tracks, dumping them into a file, and referencing them later.

It also contains a mapping table for the default font, with instrument names, etc.

Soundvault entries are meant to be easily loadable into SWDL files.

Soundvault is specified by the `skytemple_dse.soundvault.vault.Vault` class and meant to be stored as
pickled Python objects.
