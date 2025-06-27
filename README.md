# WAV Metadata Manager

A tool for managing metadata of WAV files and renaming them according to the [Universal Category System (UCS)](https://universalcategorysystem.com/) based on embedded metadata.

This tool uses a metadata and naming system inspired by Kai Paquin’s conventions, with modifications for personal workflows.

---

## 📁 Filename Structure (UCS-Style)

The general format of filenames is:

```
CatID_FXName_CreatorID_SourceID_UsedData.wav
```

**Components:**

- **CatID:** Category ID from UCS  
- **FXName:** Name of the sound or recording  
- **CreatorID:** Your creator ID (e.g., `AX` in my case)  
- **SourceID:** Project name or source identifier  
- **UsedData:** A unique ID for the file in the format `YYYYMMDD-HHMMSS` (creation date and time)
---

## 🎙️ Embedded Metadata

### BWF Metadata (`bext` chunk)

- **Description:**  
  Short summary of the recording — what is happening, descriptions of sounds, and, if possible, the location and GPS coordinates.

- **Originator:**  
  Recorder and microphone details.

---

### RIFF Metadata (`LIST` chunk)

#### Name
The `Name` field holds the `FXName` used in the filename, following UCS conventions.

---

## 🛠️ Naming Conventions

### Single Source SFX

Format:
```
TITLE (Take#) - Subtitle - Props - Verbs - Descriptive Terms
```

Example:
```
CAN - Pluck - 033 Can, Pull Tab - Pluck, Squeeze, Drag
```

**Components:**

- **TITLE:**  
  Short (1–2 words) name of the sound. Should immediately convey the general content of the recording.

- **(Take#):** *(Optional)*  
  Take number, which can include microphone distance or perspective details.

- **Subtitle:**  
  Additional context or description.

- **Props:**  
  Objects or materials used in creating the sound.

- **Verbs:**  
  Actions performed on the props.
- 
---

### Ambience Source SFX

Format:
```
SETTING - Specific Location - Primary Content in Descending Order
```

**Components:**

- **SETTING:**  
  1–3 words describing the general recording environment (e.g., Boat Wharf, Elementary School).

- **Specific Location:**  
  Precise location details such as city, region, or country.

- **Primary Content in Descending Order:**  
  List of key sonic elements, ordered by their prominence in the recording.

---

## ✅ Example for Ambience

```
PARK - Central Park, NYC - Children Playing, Birds Chirping, Distant Traffic
```

---

## 📚 References

- [Universal Category System](https://universalcategorysystem.com/)

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

