%module(package="skytemple_dse.sf2") sf2cute
%{
/* Includes the header in the wrapper code */
#include "sf2cute/file.hpp"
#include "sf2cute/generator_item.hpp"
#include "sf2cute/instrument.hpp"
#include "sf2cute/instrument_zone.hpp"
#include "sf2cute/modulator.hpp"
#include "sf2cute/modulator_item.hpp"
#include "sf2cute/modulator_key.hpp"
#include "sf2cute/preset.hpp"
#include "sf2cute/preset_zone.hpp"
#include "sf2cute/sample.hpp"
#include "sf2cute/types.hpp"
#include "sf2cute/version.hpp"
#include "sf2cute/zone.hpp"
using namespace sf2cute;
%}

/* Parse the header file to generate wrappers */
%include "std_string.i"
%include "sf2cute/file.hpp"
%include "sf2cute/generator_item.hpp"
%include "sf2cute/instrument.hpp"
%include "sf2cute/instrument_zone.hpp"
%include "sf2cute/modulator.hpp"
%include "sf2cute/modulator_item.hpp"
%include "sf2cute/modulator_key.hpp"
%include "sf2cute/preset.hpp"
%include "sf2cute/preset_zone.hpp"
%include "sf2cute/sample.hpp"
%include "sf2cute/types.hpp"
%include "sf2cute/version.hpp"
%include "sf2cute/zone.hpp"
