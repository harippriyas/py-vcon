"""
Module for vcon command line interface script functions.  Pulled out of vcon CLI
script file so that it coould more easily be tested with pytest.
"""

import os
import sys
import pathlib
import typing
import argparse
import json
import email
import email.utils
import socket
import sox
import vcon

def get_mime_type(file_name):
  """ derive mimetype from fle extension """
  path = pathlib.PurePath(file_name)
  extension = path.suffix.lower()

  print("extension: {}".format(extension), file=sys.stderr)

  if(extension == ".wav"):
    mimetype = vcon.Vcon.MIMETYPE_AUDIO_WAV

  # TODO: add: mp3, mp4 aac, ogg, 
  else:
    raise Exception("MIME type not defined for extension: {}".format(extension))

  return(mimetype)


def do_in_email(args, in_vcon):
  if(not args.emailfile[0].exists()):
    raise Exception("Email file: {} does not exist".format(args.emailfile[0]))

  # Read in the email SMTP message file
  with open(args.emailfile[0], "r") as smtp_message_file:
    smtp_message_string = smtp_message_file.read()

  # add the email message as a dialog along with its paties if not
  # already in the vcon
  in_vcon.add_dialog_inline_email_message(
    smtp_message_string,
    os.path.basename(args.emailfile[0])
    )

  return(in_vcon)

def main(argv : typing.Optional[typing.Sequence[str]] = None) -> int:
  parser = argparse.ArgumentParser("vCon operations such as construction, signing, encryption, verification, decrytpion, filtering")
  input_group = parser.add_mutually_exclusive_group()
  input_group.add_argument("-i", "--infile", metavar='infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
  input_group.add_argument("-n", "--newvcon", action="store_true")

  parser.add_argument("-o", "--outfile", metavar='outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)

  parser.add_argument(
    "-r",
    "--register-filter-plugin",
    nargs = 4,
    action = "append",
    metavar = ("register_name", "module_name", "class_name", "FilterPluginInitOptions"),
    help = "register and load a FilterPlugin as the given name from module and class and initialize using the given FilterPluginInitOptions (JSON dict string)",
    type = str,
    default = [])

  subparsers_command = parser.add_subparsers(dest="command")

  addparser = subparsers_command.add_parser("add")
  subparsers_add = addparser.add_subparsers(dest="add_command")
  add_in_recording_subparsers = subparsers_add.add_parser("in-recording")
  add_in_recording_subparsers.add_argument("recfile", metavar='recording_file', nargs=1, type=pathlib.Path, default=None)
  add_in_recording_subparsers.add_argument("start", metavar='start_time', nargs=1, type=str, default=None)
  add_in_recording_subparsers.add_argument("parties", metavar='parties', nargs=1, type=str, default=None)

  add_ex_recording_subparsers = subparsers_add.add_parser("ex-recording")
  add_ex_recording_subparsers.add_argument("recfile", metavar='recording_file', nargs=1, type=pathlib.Path, default=None)
  add_ex_recording_subparsers.add_argument("start", metavar='start_time', nargs=1, type=str, default=None)
  add_ex_recording_subparsers.add_argument("parties", metavar='parties', nargs=1, type=str, default=None)
  add_ex_recording_subparsers.add_argument("url", metavar='url', nargs=1, type=str, default=None)

  add_in_email_subparsers = subparsers_add.add_parser("in-email")
  add_in_email_subparsers.add_argument("emailfile", metavar='email_file', nargs=1, type=pathlib.Path, default=None)
  # not needed as they come from the SMTP message:
  # add_in_email_subparsers.add_argument("start", metavar='start_time', nargs="?", type=str, default=None)
  # add_in_email_subparsers.add_argument("parties", metavar='parties', nargs="?", type=str, default=None)

  extractparser = subparsers_command.add_parser("extract")
  subparsers_extract = extractparser.add_subparsers(dest="extract_command")
  extract_dialog_subparsers = subparsers_extract.add_parser("dialog")
  extract_dialog_subparsers.add_argument("index", metavar='dialog_index', nargs=1, type=int, default=None)

  filter_parser = subparsers_command.add_parser("filter")
  plugin_names = vcon.filter_plugins.FilterPluginRegistry.get_names()
  default_types = vcon.filter_plugins.FilterPluginRegistry.get_types()
  fn_help = "Name of filter plugin (e.g. {}) or default type filter plugin name (e.g. {})".format(
    ", ".join(plugin_names),
    ", ".join(default_types)
    )
  filter_parser.add_argument("filter_name", metavar="filter_plugin_name", nargs=1, type=str, help=fn_help, default=None, action="append")
  fo_help="JSON dict/object (FilterPluginOptions) with key name values which are options passed to the filter. (e.g. \'{\"a\" : 1, \"b\" : \"two\"}\' )"
  filter_parser.add_argument("-fo", "--filter-options", metavar='filter_options', nargs=1, type=str, help=fo_help, action="append")

  sign_parser = subparsers_command.add_parser("sign")
  sign_parser.add_argument("privkey", metavar='private_key_file', nargs=1, type=pathlib.Path, default=None)
  sign_parser.add_argument("pubkey", metavar='public_key_file', nargs='+', type=pathlib.Path, default=None)

  verify_parser = subparsers_command.add_parser("verify")
  verify_parser.add_argument("pubkey", metavar='public_key_file', nargs='+', type=pathlib.Path, default=None)

  encrypt_parser = subparsers_command.add_parser("encrypt")
  encrypt_parser.add_argument("pubkey", metavar='public_key_file', nargs='+', type=pathlib.Path, default=None)

  decrypt_parser = subparsers_command.add_parser("decrypt")
  decrypt_parser.add_argument("privkey", metavar='private_key_file', nargs=1, type=pathlib.Path, default=None)
  decrypt_parser.add_argument("pubkey", metavar='public_key_file', nargs=1, type=pathlib.Path, default=None)

  args = parser.parse_args(argv)

  print("args: {}".format(args), file=sys.stderr)
  print("args dir: {}".format(dir(args)), file=sys.stderr)

  print("command: {}".format(args.command), file=sys.stderr)

  for filter_plugin_registration in args.register_filter_plugin:
    print("test cli got reg info pluging: {}".format(
      filter_plugin_registration[0]
      ),
      file = sys.stderr
      )
    if(len(filter_plugin_registration) >= 5):
      init_options_json = filter_plugin_registration[4]
    else:
      init_options_json = None
    if(init_options_json is not None and init_options_json != ""):
      init_options_dict = json.loads(init_options_json)
      if(not isinstance(init_options_dict, dict)):
        print("filter init options: {} ignored, must be a valid json dict string".format(
          init_options_json),
          file = sys.stderr
          )
        sys.exit(2)
    else:
      init_options_dict = {}

    vcon.filter_plugins.FilterPluginRegistry.register(
      filter_plugin_registration[0],
      filter_plugin_registration[1],
      filter_plugin_registration[2],
      filter_plugin_registration[0],
      init_options_dict,
      replace=True)

  if(args.command == "sign"):
    print("priv key files: {}".format(len(args.privkey)), file=sys.stderr)
    if(args.privkey[0].exists()):
      print("priv key: {} exists".format(str(args.privkey[0])), file=sys.stderr)
    else:
      print("priv key: {} does NOT exist".format(str(args.privkey[0])), file=sys.stderr)

    print("pub key files: {}".format(len(args.pubkey)), file=sys.stderr)

  if(args.command == "verify"):
    if(args.pubkey[0].exists()):
      print("pub key: {} exists".format(str(args.pubkey[0])), file=sys.stderr)
    else:
      print("pub key: {} does NOT exist".format(str(args.pubkey[0])), file=sys.stderr)

  if(args.command == "encrypt"):
    if(args.pubkey[0].exists()):
      print("pub key: {} exists".format(str(args.pubkey[0])), file=sys.stderr)
    else:
      print("pub key: {} does NOT exist".format(str(args.pubkey[0])), file=sys.stderr)

  if(args.command == "decrypt"):
    if(args.pubkey[0].exists()):
      print("pub key: {} exists".format(str(args.pubkey[0])), file=sys.stderr)
    else:
      print("pub key: {} does NOT exist".format(str(args.pubkey[0])), file=sys.stderr)
    if(args.privkey[0].exists()):
      print("priv key: {} exists".format(str(args.privkey[0])), file=sys.stderr)
    else:
      print("priv key: {} does NOT exist".format(str(args.privkey[0])), file=sys.stderr)

  if(args.command == "add"):
    print("add: {}".format(args.add_command), file=sys.stderr)

  """
  Options: 
    [-n | -i <file_name>][-o <file_name>][-r filter_plugin_name plugin_module plugin_class_name [-r ...]]
 
  Commands:
    add in-recording <file_name> <start_date> <parties>
    add ex-recording <file_name> <start_date> <parties> <url>
 
    filter filter-name [-fo filter-options-dict] 

    sign private_key x5c1[, x5c2]... 
  
    verify ca_cert
  
    encrypt x5c1[, x5c2]... signing_private_key
  
    decrypt private_key, ca_cert
  
  """

  print("reading", file=sys.stderr)

  print("out: {}".format(type(args.outfile)), file=sys.stderr)
  print("in: {}".format(type(args.infile)), file=sys.stderr)
  print("new in {}".format(args.newvcon), file=sys.stderr)
  print("filter plugin registrations in {}".format(args.register_filter_plugin), file=sys.stderr)
  in_vcon = vcon.Vcon()
  if(not args.newvcon):
    in_vcon_json = args.infile.read()
    if(in_vcon_json is not None and len(in_vcon_json) > 0):
      in_vcon.loads(in_vcon_json)
  else:
    pass

  # Use default serialization for state of vCon
  signed_json = True

  # By default we output the vCon at the end
  stdout_vcon = True

  if(args.command == "sign"):
    in_vcon.sign(args.privkey[0], args.pubkey)

  elif(args.command == "verify"):
    print("state: {}".format(in_vcon._state), file=sys.stderr)
    in_vcon.verify(args.pubkey)

    # Assuming that generally if someone is verifying the vCon, they want the
    # unsigned JSON version as output.
    signed_json = False

  elif(args.command == "filter"):
    plugin_name = args.filter_name[0][0].strip(" '\"")
    print("filter name: \"{}\"".format(plugin_name), file=sys.stderr)
    if(args.filter_options is not None):
      try:
        filter_options_dict = json.loads(args.filter_options[0][0].strip(" '\""))
      except Exception as opt_error:
        print(opt_error, file=sys.stderr)
        print("filter options: {}".format(args.filter_options))
        filter_options_dict = None
      if(not isinstance(filter_options_dict, dict)):
        print("filter_options should be a well formed dict.  Got: {}".format(args.filter_options[0][0]), file=sys.stderr)
        sys.exit(2)
    else:
      filter_options_dict = {}
    print("filter options: \"{}\"".format(filter_options_dict), file=sys.stderr)
    try:
      plugin = vcon.filter_plugins.FilterPluginRegistry.get(plugin_name, True, True)
      print("got plugin for: {}".format(plugin), file=sys.stderr)
      if(plugin is None):
        raise Exception("should not get here, exception should have been raised in get()")
    except Exception as pname_error:
      names = vcon.filter_plugins.FilterPluginRegistry.get_names()
      print("filter name: {} not found, the following filters are registered: {}".format(
        plugin_name,
        names
        ),
        file = sys.stdout
        )

      raise pname_error

    # send print statements that we want to go to stderr
    #
    # Leaving this here commented out for diagnostic purposes.  I kind of
    # like it that the unit test fails if there is any print to stdout
    # noise to force clean up.
    #with contextlib.redirect_stdout(sys.stderr):

    if(plugin is None):
      raise Exception("Should not get here")

    options = plugin.options_type(**filter_options_dict)
    in_vcon = in_vcon.filter(plugin_name, options)

  elif(args.command == "encrypt"):
    print("state: {}".format(in_vcon._state), file=sys.stderr)
    in_vcon.encrypt(args.pubkey[0])

  elif(args.command == "decrypt"):
    print("state: {}".format(in_vcon._state), file=sys.stderr)
    in_vcon.decrypt(args.privkey[0], args.pubkey[0])

  elif(args.command == "add"):
    if(args.add_command in ["in-recording", "ex-recording"]):
      if(not args.recfile[0].exists()):
        raise Exception("Recording file: {} does not exist".format(args.recfile[0]))

      sox_info = sox.file_info.info(str(args.recfile[0]))
      duration = sox_info["duration"]
      mimetype = get_mime_type(args.recfile[0])

      with open(args.recfile[0], 'rb') as file_handle:
        body = file_handle.read()

      parties_object = json.loads(args.parties[0])

      if(args.add_command == "in-recording"):
        in_vcon.add_dialog_inline_recording(body, args.start[0], duration, parties_object,
          mimetype, str(args.recfile[0]))

      elif(args.add_command == "ex-recording"):
        in_vcon.add_dialog_external_recording(body, args.start[0], duration, parties_object,
          args.url[0], mimetype, str(args.recfile[0]))

    elif(args.add_command == "in-email"):
      in_vcon = do_in_email(args, in_vcon)


  elif(args.command == "extract"):
    if(args.extract_command == "dialog"):
      if(not isinstance(args.index[0], int)):
        raise AttributeError("Dialog index should be type int, not {}".format(type(args.index[0])))

      dialog_index = args.index[0]
      num_dialogs = len(in_vcon.dialog)
      if(dialog_index > num_dialogs):
        raise AttributeError("Dialog index: {} must be less than the number of dialog in the vCon: {}".format(dialog_index, num_dialogs))

      recording_bytes = in_vcon.decode_dialog_inline_body(dialog_index)
      stdout_vcon = False
      if(isinstance(recording_bytes, bytes)):
        args.outfile.buffer.write(recording_bytes)
      else:
        args.outfile.write(recording_bytes)

  #print("vcon._vcon_dict: {}".format(in_vcon._vcon_dict))
  if(stdout_vcon):
    if(in_vcon._state == vcon.VconStates.UNSIGNED and (in_vcon.uuid is None or len(in_vcon.uuid) < 1)):
      in_vcon.set_uuid(socket.gethostname() + ".vcon.dev")
    out_vcon_json = in_vcon.dumps(signed=signed_json)
    args.outfile.write(out_vcon_json)

  return(0)

