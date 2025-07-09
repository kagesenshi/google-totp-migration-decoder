import base64
import urllib.parse
from google.protobuf import descriptor_pb2
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf.message_factory import GetMessageClass
import cv2
from pyzbar import pyzbar
import argparse

# Dynamically define the MigrationPayload descriptor
def get_migration_descriptor():
    pool = _descriptor_pool.DescriptorPool()
    file_desc_proto = descriptor_pb2.FileDescriptorProto()
    file_desc_proto.name = 'migration.proto'
    file_desc_proto.package = 'otp'

    # OTPParameters
    otp_parameters = file_desc_proto.message_type.add()
    otp_parameters.name = 'OTPParameters'
    otp_parameters.field.add(name='secret', number=1, type=12, label=1)  # bytes
    otp_parameters.field.add(name='name', number=2, type=9, label=1)     # string
    otp_parameters.field.add(name='issuer', number=3, type=9, label=1)   # string
    otp_parameters.field.add(name='algorithm', number=4, type=14, label=1, type_name='.otp.Algorithm')
    otp_parameters.field.add(name='digits', number=5, type=14, label=1, type_name='.otp.Digits')
    otp_parameters.field.add(name='type', number=6, type=14, label=1, type_name='.otp.OTPType')
    otp_parameters.field.add(name='counter', number=7, type=4, label=1)  # uint64

    # MigrationPayload
    migration_payload = file_desc_proto.message_type.add()
    migration_payload.name = 'MigrationPayload'
    migration_payload.field.add(name='otp_parameters', number=1, type=11, label=3, type_name='.otp.OTPParameters')
    migration_payload.field.add(name='version', number=2, type=5, label=1)      # int32
    migration_payload.field.add(name='batch_size', number=3, type=5, label=1)   # int32
    migration_payload.field.add(name='batch_index', number=4, type=5, label=1)  # int32
    migration_payload.field.add(name='batch_id', number=5, type=5, label=1)     # int32

#    # Enums
    algo_enum = file_desc_proto.enum_type.add()
    algo_enum.name = 'Algorithm'
    for i, name in enumerate(['ALGORITHM_UNSPECIFIED', 'ALGORITHM_SHA1', 'ALGORITHM_SHA256', 'ALGORITHM_SHA512', 'ALGORITHM_MD5']):
        algo_enum.value.add(name=name, number=i)

    digits_enum = file_desc_proto.enum_type.add()
    digits_enum.name = 'Digits'
    for i, name in enumerate(['DIGITS_UNSPECIFIED', 'DIGITS_6', 'DIGITS_8']):
        digits_enum.value.add(name=name, number=i)

    type_enum = file_desc_proto.enum_type.add()
    type_enum.name = 'OTPType'
    for i, name in enumerate(['OTP_TYPE_UNSPECIFIED', 'HOTP', 'TOTP']):
        type_enum.value.add(name=name, number=i)

    file_desc = pool.Add(file_desc_proto)
    return file_desc.message_types_by_name['MigrationPayload']

# Decode the URL and extract OTP entries
def decode_migration_url(url: str):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'otpauth-migration':
        raise ValueError("Invalid URL scheme")

    query = urllib.parse.parse_qs(parsed.query)
    if 'data' not in query:
        raise ValueError("Missing data parameter")

    data_b64 = query['data'][0]
    raw = base64.urlsafe_b64decode(data_b64 + '==')

    descriptor = get_migration_descriptor()
    cls = GetMessageClass(descriptor)
    payload = cls()
    payload.ParseFromString(raw)
    result = []
    for entry in payload.otp_parameters:
        otp_entry = {
            'name': entry.name,
            'issuer': entry.issuer,
            'secret': base64.b32encode(entry.secret).decode(),
            'type': entry.type,
            'algorithm': entry.algorithm,
            'digits': entry.digits,
            'counter': entry.counter if hasattr(entry, 'counter') else None
        }
        result.append(otp_entry)

    return result

def extract_qr(image_path):
    image = cv2.imread(image_path)
    result = pyzbar.decode(image)
    if not result:
        return []
    urls = [r.data.decode('utf8') for r in result]
    return [url for url in urls if url.startswith('otpauth-migration://')]

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('qr_image', nargs='+')
    args = parser.parse_args()
    
    accounts = []
    for image_path in args.qr_image:
        for url in extract_qr(image_path):
            accounts += decode_migration_url(url)
    for i, acc in enumerate(accounts, 1):
        print(f"\nAccount {i}:")
        for k, v in acc.items():
            print(f"  {k}: {v}")

