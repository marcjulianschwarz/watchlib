ME_KEYS = {
    "Date of Birth": "HKCharacteristicTypeIdentifierDateOfBirth",
    "Sex": "HKCharacteristicTypeIdentifierBiologicalSex",
    "Blood Type": "HKCharacteristicTypeIdentifierBloodType",
    "Skin Type": "HKCharacteristicTypeIdentifierFitzpatrickSkinType",
    "Cardio Fitness Medication": "HKCharacteristicTypeIdentifierCardioFitnessMedicationsUse",
}

SEX_MAP = {"HKBiologicalSexMale": "Male", "HKBiologicalSexFemale": "Female"}

BLOOD_TYPE_MAP = {"HKBloodTypeNotSet": "No blood type set."}

SKIN_TYPE_MAP = {"HKFitzpatrickSkinTypeNotSet": "No skin type set."}

MEDICATION_MAP = {"HKMedicationUsageNotSet": "No medication set."}

HK_WORKOUT_ACTIVITY_TYPE_MAP = {
    "HKWorkoutActivityTypeCycling": "Cycling",
    "HKWorkoutActivityTypeRunning": "Running",
    "HKWorkoutActivityTypeWalking": "Walking",
    "HKWorkoutActivityTypeSwimming": "Swimming",
    "HKWorkoutActivityTypeHiking": "Hiking",
    "HKWorkoutActivityTypeTraditionalStrengthTraining": "Traditional Strength Training",
    "HKWorkoutActivityTypeHighIntensityIntervalTraining": "High Intensity Interval Training",
    "HKWorkoutActivityTypeYoga": "Yoga",
    "HKWorkoutActivityTypeSkatingSports": "Skating Sports",
    "HKWorkoutActivityTypeOther": "Other",
}

HK_WORKOUT_DISTANCE_MAP = {
    "HKQuantityTypeIdentifierDistanceCycling": "Distance Cycling",
}

HK_WORKOUT_DISTANCE_KEYS = list(HK_WORKOUT_DISTANCE_MAP.keys())
