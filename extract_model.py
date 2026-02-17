import bz2

input_file = "shape_predictor_68_face_landmarks.dat.bz2"
output_file = "shape_predictor_68_face_landmarks.dat"

with bz2.open(input_file, "rb") as f_in:
    data = f_in.read()

with open(output_file, "wb") as f_out:
    f_out.write(data)

print("Extraction completed successfully.")
