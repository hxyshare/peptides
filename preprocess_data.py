# -*- coding: utf-8 -*-
import deepnovo_config
import re


def inspect_file_location(data_format, input_file):
  """TODO(nh2tran): docstring."""

  print("inspect_file_location(), input_file = ", input_file)

  if data_format == "msp":
    keyword = "Name"
  elif data_format == "mgf":
    keyword = "BEGIN IONS"

  spectra_file_location = []
  with open(input_file, mode="r") as file_handle:
    line = True
    while line:
      file_location = file_handle.tell()
      line = file_handle.readline()
      if keyword in line:
        spectra_file_location.append(file_location)

  return spectra_file_location


def read_spectra(file_handle, data_format, spectra_locations):
  """TODO(nh2tran): docstring."""

  print("read_spectra()")

  #~ # for testing
  #~ test_time = 0.0

  data_set = [[] for _ in deepnovo_config._buckets]
  counter = 0
  counter_skipped = 0
  counter_skipped_mod = 0
  counter_skipped_len = 0
  counter_skipped_mass = 0
  counter_skipped_mass_precision = 0
  avg_peak_count = 0.0
  avg_peptide_len = 0.0

  if data_format == "mgf":
    keyword = "BEGIN IONS"

  for location in spectra_locations:

    file_handle.seek(location)
    line = file_handle.readline()
    assert (keyword in line), "ERROR: read_spectra(); wrong format"

    unknown_modification = False

    # READ AN ENTRY
    if data_format == "mgf":

      # header TITLE
      line = file_handle.readline()

      # header PEPMASS
      line = file_handle.readline()
      peptide_ion_mz = float(re.split('=|\n', line)[1])

      # header CHARGE
      line = file_handle.readline()
      charge = float(re.split('=|\+', line)[1]) # pylint: disable=anomalous-backslash-in-string,line-too-long

      # header SCANS
      line = file_handle.readline()
      #~ scan = int(re.split('=', line)[1])
      scan = re.split('=|\n', line)[1]

      # header RTINSECONDS
      line = file_handle.readline()

      # header SEQ
      line = file_handle.readline()
      raw_sequence = re.split('=|\n|\r', line)[1]
      raw_sequence_len = len(raw_sequence)
      print(raw_sequence)
      peptide = []
      index = 0
      while index < raw_sequence_len:
        if raw_sequence[index] == "(":
          if peptide[-1] == "C" and raw_sequence[index:index+8] == "(+57.02)":
            peptide[-1] = "Cmod"
            index += 8
          elif peptide[-1] == 'M' and raw_sequence[index:index+8] == "(+15.99)":
            peptide[-1] = 'Mmod'
            index += 8
          elif peptide[-1] == 'N' and raw_sequence[index:index+6] == "(+.98)":
            peptide[-1] = 'Nmod'
            index += 6
          elif peptide[-1] == 'Q' and raw_sequence[index:index+6] == "(+.98)":
            peptide[-1] = 'Qmod'
            index += 6
          else: # unknown modification
          #~ elif ("".join(raw_sequence[index:index+8])=="(+42.01)"):
            #~ print("ERROR: unknown modification!")
            #~ print("raw_sequence = ", raw_sequence)
            #~ sys.exit()
            unknown_modification = True
            break
        else:
          peptide.append(raw_sequence[index])
          index += 1

      # skip if unknown_modification
      if unknown_modification:
        counter_skipped += 1
        counter_skipped_mod += 1
        continue

      # skip if neutral peptide_mass > MZ_MAX(3000.0)
      peptide_mass = peptide_ion_mz*charge - charge*deepnovo_config.mass_H
      if peptide_mass > deepnovo_config.MZ_MAX:
        counter_skipped += 1
        counter_skipped_mass += 1
        continue

      # TRAINING-SKIP: skip if peptide length > MAX_LEN(30)
      # TESTING-ERROR: not allow peptide length > MAX_LEN(50)
      peptide_len = len(peptide)
      if peptide_len > deepnovo_config.MAX_LEN:
        #~ print("ERROR: peptide_len {0} exceeds MAX_LEN {1}".format(
            #~ peptide_len,
            #~ deepnovo_config.MAX_LEN))
        #~ sys.exit()
        counter_skipped += 1
        counter_skipped_len += 1
        continue

      # DEPRECATED-TRAINING-ONLY: testing peptide_mass & sequence_mass
      sequence_mass = sum(deepnovo_config.mass_AA[aa] for aa in peptide)
      sequence_mass += deepnovo_config.mass_N_terminus + deepnovo_config.mass_C_terminus
      if (abs(peptide_mass-sequence_mass)
          > deepnovo_config.PRECURSOR_MASS_PRECISION_INPUT_FILTER):
        #~ print("ERROR: peptide_mass and sequence_mass not matched")
        #~ print("peptide = ", peptide)
        #~ print("peptide_list_mod = ", peptide_list_mod)
        #~ print("peptide_list = ", peptide_list)
        #~ print("peptide_ion_mz = ",peptide_ion_mz)
        #~ print("charge = ", charge)
        #~ print("peptide_mass  ", peptide_mass)
        #~ print("sequence_mass ", sequence_mass)
        #~ sys.exit()
        counter_skipped_mass_precision += 1
        counter_skipped += 1
        continue

      # read spectrum
      spectrum_mz = []
      spectrum_intensity = []
      line = file_handle.readline()
      while not "END IONS" in line:
        # parse pairs of "mz intensity"
        mz, intensity = re.split(' |\n', line)[:2]
        intensity_float = float(intensity)
        mz_float = float(mz)
        if mz_float > deepnovo_config.MZ_MAX: # skip this peak
          line = file_handle.readline()
          continue
        spectrum_mz.append(mz_float)
        spectrum_intensity.append(intensity_float)
        line = file_handle.readline()

    # AN ENTRY FOUND
    counter += 1
    if counter % 10000 == 0:
      print("  reading peptide %d" % counter)

    # Average number of peaks per spectrum
    peak_count = len(spectrum_mz)
    avg_peak_count += peak_count

    # Average peptide length
    avg_peptide_len += peptide_len

  #~ # for testing
  #~ print("test_time = {0:.2f}".format(test_time))

  print("  total peptide read %d" % counter)
  print("  total peptide skipped %d" % counter_skipped)
  print("  total peptide skipped by mod %d" % counter_skipped_mod)
  print("  total peptide skipped by len %d" % counter_skipped_len)
  print("  total peptide skipped by mass %d" % counter_skipped_mass)
  print("  total peptide skipped by mass precision %d"
        % counter_skipped_mass_precision)

  print("  average #peaks per spectrum %.1f" % (avg_peak_count/counter))
  print("  average peptide length %.1f" % (avg_peptide_len/counter))

  return data_set, counter


spectra_file_location_valid = inspect_file_location(
       deepnovo_config.data_format,
       deepnovo_config.input_file_train)

#文件指针的位置，也就是begin开始的位置字节，或者是字符
print(spectra_file_location_valid)
with open(deepnovo_config.input_file_train, 'r') as file_handle:
    test_set, _ = read_spectra(file_handle,
                               deepnovo_config.data_format,
                               spectra_file_location_valid)

