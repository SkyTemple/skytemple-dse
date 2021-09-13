/// @file
/// SoundFont 2 File class header.
///
/// @author gocha <https://github.com/gocha>
/// Modified by Capypara for use with Swig

#ifndef SF2CUTE_FILE_HPP_
#define SF2CUTE_FILE_HPP_

#include <algorithm>
#include <memory>
#include <utility>
#include <functional>
#include <vector>
#include <unordered_map>

#include "types.hpp"

namespace sf2cute {

class SFSample;
class SFInstrumentZone;
class SFInstrument;
class SFPresetZone;
class SFPreset;
class SoundFont;

/// The SoundFont class represents a SoundFont file.
class SoundFont {
public:
  /// Constructs a new empty SoundFont.
  SoundFont();

  /// Constructs a new copy of specified SoundFont.
  /// @param origin a SoundFont object.
  SoundFont(const SoundFont & origin);

  /// Copy-assigns a new value to the SoundFont, replacing its current contents.
  /// @param origin a SoundFont object.
  SoundFont & operator=(const SoundFont & origin);

  /// Acquires the contents of specified SoundFont.
  /// @param origin a SoundFont object.
  SoundFont(SoundFont && origin) noexcept;

  /// Move-assigns a new value to the SoundFont, replacing its current contents.
  /// @param origin a SoundFont object.
  SoundFont & operator=(SoundFont && origin) noexcept;

  /// Destructs the SoundFont.
  ~SoundFont() = default;

  /// Returns the list of presets.
  /// @return the list of presets assigned to the SoundFont.
  const std::vector<std::shared_ptr<SFPreset>> & presets() const noexcept {
    return presets_;
  }

  /// Adds a new preset to the SoundFont.
  /// @param args the arguments for the SFPreset constructor.
  /// @return the new SFPreset object.
  /// @throws std::invalid_argument Preset has already been owned by another file.
  template<typename ... Args>
  std::shared_ptr<SFPreset> NewPreset(Args && ... args) {
    std::shared_ptr<SFPreset> preset =
      std::make_shared<SFPreset>(std::forward<Args>(args)...);
    AddPreset(preset);
    return std::move(preset);
  }

  /// Adds a preset to the SoundFont.
  /// @param preset a preset to be assigned to the SoundFont.
  /// @throws std::invalid_argument Preset has already been owned by another file.
  void AddPreset(std::shared_ptr<SFPreset> preset);

  /// Removes a preset from the SoundFont.
  /// @param position the preset to remove.
  void RemovePreset(
      std::vector<std::shared_ptr<SFPreset>>::const_iterator position);

  /// Removes presets from the SoundFont.
  /// @param first the first preset to remove.
  /// @param last the last preset to remove.
  void RemovePreset(
      std::vector<std::shared_ptr<SFPreset>>::const_iterator first,
      std::vector<std::shared_ptr<SFPreset>>::const_iterator last);

  /// Removes presets from the SoundFont.
  /// @param predicate unary predicate which returns true if the preset should be removed.
  void RemovePresetIf(
      std::function<bool(const std::shared_ptr<SFPreset> &)> predicate);

  /// Removes all of the presets.
  void ClearPresets() noexcept;

  /// Returns the list of instruments.
  /// @return the list of instruments assigned to the SoundFont.
  const std::vector<std::shared_ptr<SFInstrument>> & instruments() const noexcept {
    return instruments_;
  }

  /// Adds a new instrument to the SoundFont.
  /// @param args the arguments for the SFInstrument constructor.
  /// @return the new SFInstrument object.
  /// @throws std::invalid_argument Instrument has already been owned by another file.
  template<typename ... Args>
  std::shared_ptr<SFInstrument> NewInstrument(Args && ... args) {
    std::shared_ptr<SFInstrument> instrument =
      std::make_shared<SFInstrument>(std::forward<Args>(args)...);
    AddInstrument(instrument);
    return std::move(instrument);
  }

  /// Adds an instrument to the SoundFont.
  /// @param instrument an instrument to be assigned to the SoundFont.
  /// @throws std::invalid_argument Instrument has already been owned by another file.
  void AddInstrument(std::shared_ptr<SFInstrument> instrument);

  /// Removes an instrument from the SoundFont.
  /// @param position the instrument to remove.
  void RemoveInstrument(
      std::vector<std::shared_ptr<SFInstrument>>::const_iterator position);

  /// Removes instruments from the SoundFont.
  /// @param first the first instrument to remove.
  /// @param last the last instrument to remove.
  void RemoveInstrument(
      std::vector<std::shared_ptr<SFInstrument>>::const_iterator first,
      std::vector<std::shared_ptr<SFInstrument>>::const_iterator last);

  /// Removes instruments from the SoundFont.
  /// @param predicate unary predicate which returns true if the instrument should be removed.
  void RemoveInstrumentIf(
      std::function<bool(const std::shared_ptr<SFInstrument> &)> predicate);

  /// Removes all of the instruments.
  void ClearInstruments() noexcept;

  /// Returns the list of samples.
  /// @return the list of samples assigned to the SoundFont.
  const std::vector<std::shared_ptr<SFSample>> & samples() const noexcept {
    return samples_;
  }

  /// Adds a new sample to the SoundFont.
  /// @param args the arguments for the SFSample constructor.
  /// @return the new SFSample object.
  /// @throws std::invalid_argument Sample has already been owned by another file.
  template<typename ... Args>
  std::shared_ptr<SFSample> NewSample(Args && ... args) {
    std::shared_ptr<SFSample> sample =
      std::make_shared<SFSample>(std::forward<Args>(args)...);
    AddSample(sample);
    return std::move(sample);
  }

  /// Adds a sample to the SoundFont.
  /// @param sample a sample to be assigned to the SoundFont.
  /// @throws std::invalid_argument Sample has already been owned by another file.
  void AddSample(std::shared_ptr<SFSample> sample);

  /// Removes a sample from the SoundFont.
  /// @param position the sample to remove.
  void RemoveSample(
      std::vector<std::shared_ptr<SFSample>>::const_iterator position);

  /// Removes samples from the SoundFont.
  /// @param first the first sample to remove.
  /// @param last the last sample to remove.
  void RemoveSample(
      std::vector<std::shared_ptr<SFSample>>::const_iterator first,
      std::vector<std::shared_ptr<SFSample>>::const_iterator last);

  /// Removes samples from the SoundFont.
  /// @param predicate unary predicate which returns true if the sample should be removed.
  void RemoveSampleIf(
      std::function<bool(const std::shared_ptr<SFSample> &)> predicate);

  /// Removes all of the samples.
  void ClearSamples() noexcept;

  /// Returns the target sound engine.
  /// @return the target sound engine name.
  const std::string & sound_engine() const noexcept {
    return sound_engine_;
  }

  /// Sets the target sound engine.
  /// @param sound_engine the target sound engine name.
  void set_sound_engine(std::string sound_engine) {
    sound_engine_ = std::move(sound_engine);
  }

  /// Returns the SoundFont bank name.
  /// @return the SoundFont bank name.
  const std::string & bank_name() const noexcept {
    return bank_name_;
  }

  /// Sets the SoundFont bank name.
  /// @param bank_name the SoundFont bank name.
  void set_bank_name(std::string bank_name) {
    bank_name_ = std::move(bank_name);
  }

  /// Returns true if the SoundFont has a Sound ROM name.
  /// @return true if the SoundFont has a Sound ROM name.
  bool has_rom_name() const noexcept {
    return !rom_name_.empty();
  }

  /// Returns the Sound ROM name.
  /// @return the Sound ROM name.
  const std::string & rom_name() const noexcept {
    return rom_name_;
  }

  /// Sets the Sound ROM name.
  /// @param rom_name the Sound ROM name.
  void set_rom_name(std::string rom_name) {
    rom_name_ = std::move(rom_name);
  }

  /// Resets the Sound ROM name.
  void reset_rom_name() noexcept {
    rom_name_.clear();
  }

  /// Returns true if the SoundFont has a Sound ROM version.
  /// @return true if the SoundFont has a Sound ROM version.
  bool has_rom_version() const noexcept {
    return has_rom_version_;
  }

  /// Returns the Sound ROM version.
  /// @return the Sound ROM version.
  SFVersionTag rom_version() const noexcept {
    return rom_version_;
  }

  /// Sets the Sound ROM version.
  /// @param rom_version the Sound ROM version.
  void set_rom_version(SFVersionTag rom_version) {
    rom_version_ = std::move(rom_version);
    has_rom_version_ = true;
  }

  /// Resets the Sound ROM version.
  void reset_rom_version() noexcept {
    has_rom_version_ = false;
  }

  /// Returns true if the SoundFont has a date of creation of the bank.
  /// @return true if the SoundFont has a date of creation of the bank.
  bool has_creation_date() const noexcept {
    return !creation_date_.empty();
  }

  /// Returns the date of creation of the bank.
  /// @return the date of creation of the bank.
  const std::string & creation_date() const noexcept {
    return creation_date_;
  }

  /// Sets the date of creation of the bank.
  /// @param creation_date the date of creation of the bank.
  void set_creation_date(std::string creation_date) {
    creation_date_ = std::move(creation_date);
  }

  /// Resets the date of creation of the bank.
  void reset_creation_date() noexcept {
    creation_date_.clear();
  }

  /// Returns true if the SoundFont has the sound designers and engineers information for the bank.
  /// @return true if the SoundFont has the sound designers and engineers information for the bank.
  bool has_engineers() const noexcept {
    return !engineers_.empty();
  }

  /// Returns the sound designers and engineers for the bank.
  /// @return the sound designers and engineers for the bank.
  const std::string & engineers() const noexcept {
    return engineers_;
  }

  /// Sets the sound designers and engineers for the bank.
  /// @param engineers the sound designers and engineers for the bank.
  void set_engineers(std::string engineers) {
    engineers_ = std::move(engineers);
  }

  /// Resets the sound designers and engineers for the bank.
  void reset_engineers() noexcept {
    engineers_.clear();
  }

  /// Returns true if the SoundFont has a product name for which the bank was intended.
  /// @return true if the SoundFont has a product name for which the bank was intended.
  bool has_product() const noexcept {
    return !product_.empty();
  }

  /// Returns the product name for which the bank was intended.
  /// @return the product name for which the bank was intended.
  const std::string & product() const noexcept {
    return product_;
  }

  /// Sets the product name for which the bank was intended.
  /// @param product the product name for which the bank was intended.
  void set_product(std::string product) {
    product_ = std::move(product);
  }

  /// Resets the product name for which the bank was intended.
  void reset_product() noexcept {
    product_.clear();
  }

  /// Returns true if the SoundFont has any copyright message.
  /// @return true if the SoundFont has any copyright message.
  bool has_copyright() const noexcept {
    return !copyright_.empty();
  }

  /// Returns the copyright message.
  /// @return the copyright message.
  const std::string & copyright() const noexcept {
    return copyright_;
  }

  /// Sets the copyright message.
  /// @param copyright the copyright message.
  void set_copyright(std::string copyright) {
    copyright_ = std::move(copyright);
  }

  /// Resets the copyright message.
  void reset_copyright() noexcept {
    copyright_.clear();
  }

  /// Returns true if the SoundFont has any comments on the bank.
  /// @return true if the SoundFont has any comments on the bank.
  bool has_comment() const noexcept {
    return !comment_.empty();
  }

  /// Returns the comments on the bank.
  /// @return the comments on the bank.
  const std::string & comment() const noexcept {
    return comment_;
  }

  /// Sets the comments on the bank.
  /// @param comment the comments on the bank.
  void set_comment(std::string comment) {
    comment_ = std::move(comment);
  }

  /// Resets the comments on the bank.
  void reset_comment() noexcept {
    comment_.clear();
  }

  /// Returns true if the SoundFont the information of SoundFont tools used to create and alter the bank.
  /// @return true if the SoundFont the information of SoundFont tools used to create and alter the bank.
  bool has_software() const noexcept {
    return !software_.empty();
  }

  /// Returns the SoundFont tools used to create and alter the bank.
  /// @return the SoundFont tools used to create and alter the bank.
  const std::string & software() const noexcept {
    return software_;
  }

  /// Sets the SoundFont tools used to create and alter the bank.
  /// @param software the SoundFont tools used to create and alter the bank.
  void set_software(std::string software) {
    software_ = std::move(software);
  }

  /// Resets the SoundFont tools used to create and alter the bank.
  void reset_software() noexcept {
    software_.clear();
  }

  /// Writes the SoundFont to a file.
  /// @param filename the name of the file to write to.
  /// @throws std::logic_error The SoundFont has a structural error.
  /// @throws std::ios_base::failure An I/O error occurred.
  void Write(const std::string & filename);

  /// Writes the SoundFont to an output stream.
  /// @param out the output stream to write to.
  void Write(std::ostream & out);

  /// @copydoc SoundFont::Write(std::ostream &)
  void Write(std::ostream && out);
};

} // namespace sf2cute

#endif // SF2CUTE_FILE_HPP_
