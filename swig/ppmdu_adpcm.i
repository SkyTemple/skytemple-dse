%module(package="skytemple_dse") ppmdu_adpcm
%{
/* Includes the header in the wrapper code */
#include "src_ppmdu_adpcm/adpcm.hpp"
using namespace audio;
%}

/* Parse the header file to generate wrappers */
%include "std_string.i"
%include <stdint.i>
%include "std_vector.i"
namespace std {
   %template(Uint8Vector) vector<uint8_t>;
   %template(Int16Vector) vector<int16_t>;
}
%include "src_ppmdu_adpcm/adpcm.hpp"
