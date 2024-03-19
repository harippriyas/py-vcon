
<sub><sup>^This document is generated.  Do not edit directly.</sup></sub>
<!--- generated by tests/test_processor_docs.py --->

# vCon Processor Framework and Plugins

## Table of Contents
 + [Introduction](#introduction)
 + [Processor Classes](#processors)
  * [py_vcon_server.processor.builtin.deepgram.Deepgram](#py_vcon_serverprocessorbuiltindeepgramdeepgram)
  * [py_vcon_server.processor.builtin.openai.OpenAiChatCompletion](#py_vcon_serverprocessorbuiltinopenaiopenaichatcompletion)
  * [py_vcon_server.processor.builtin.whisper.Whisper](#py_vcon_serverprocessorbuiltinwhisperwhisper)

 + [Processor Initialization Options Classes](#processor-initialization-options-classes)
  * [py_vcon_server.processor.builtin.deepgram.DeepgramInitOptions](#py_vcon_serverprocessorbuiltindeepgramdeepgraminitoptions)
  * [py_vcon_server.processor.builtin.openai.OpenAiChatCompletionInitOptions](#py_vcon_serverprocessorbuiltinopenaiopenaichatcompletioninitoptions)
  * [py_vcon_server.processor.builtin.whisper.WhisperInitOptions](#py_vcon_serverprocessorbuiltinwhisperwhisperinitoptions)

 + [Processor Options Classes](#processor-options-classes)
  * [py_vcon_server.processor.builtin.deepgram.DeepgramOptions](#py_vcon_serverprocessorbuiltindeepgramdeepgramoptions)
  * [py_vcon_server.processor.builtin.openai.OpenAiChatCompletionOptions](#py_vcon_serverprocessorbuiltinopenaiopenaichatcompletionoptions)
  * [py_vcon_server.processor.builtin.whisper.WhisperOptions](#py_vcon_serverprocessorbuiltinwhisperwhisperoptions)


## Introduction

TBD

# Processor Classes

## py_vcon_server.processor.VconProcessor 

 - **Name:** VconProcessor 
 - **Summary:** Abstract VconProcessor class


  Abstract base class to all vCon processors.

  A vCon Processor generally takes zero or more Vcons as input
  and produces some sort of output which may include:

    * A modification of one or more of the input vCons
    * The creation of one or more new Vcons
    * An extraction of data from the input
    * Emmition of a report (e.g. via email or slack)

  **VconProcessor**s may be sequenced together (1 or more)
  in a **Pipeline**.  A **VconProcessorIO** object is provided as
  input to the first **VconProcessor** which outputs a
  **VconProcessorIO** that become the input to the next **VconProcessor**
  in the **Pipeline** and so on.

  The **VconProcessor** contains the method **process** which performs
  the work.  It takes a **VconProcessorIO** object as input which contains
  the zero or vCon.  The ** process** method also takes a
  **VconProcessorOptions** object which is where additional input 
  parameters are provided as defined by the **VconProcessor**.  The
  **processor** method always provides output in the return in
  the form of a **VconProcessorIO** object.  Typically this is the same
  PipelilneIO that was input with some or no modification.  If
  the input **VconProcessorIO** is not provided as ouput (if the
  **VconProcessorIO** was modified by prior **VconProcessor**s in
  the **Pipeline**) any created or modified vCons from the input
  will be lost and not saved to the **VconStorage** database.  Care
  should be made that this is intensional.

  A concrete **VconProcessor** derives from **VconProcessor** and implements
  the abstract methods.  If it requires or has optional additional
  input parameters, it defines a subclass of the **VconProcessorOptions**
  class.  The derived **VconProcessorOptions** class for the derived
  **VconProcessor** serves to document the additional input parameters
  and helps to validate the input.

  A well behaved VconProcessor does not modify the VconStorage
  database at all.  Vcons are modified in the **VconProcessorIO** input
  and pass on as output.  It is up to the invoker of the **process**
  method to decide when to commit the changed to the **VconStorage** database.
  For example after all **VconProcessors** in a **Pipeline** sequence
  have been processed.  The **VconProcessorIO** keeps track of **Vcon**s
  that have been changed to ease the decision of what needs to be commited.

  A **VconProcessor** is typically dynamically loaded at startup and gets
  registered in the **VconProcessorRegistry**.  A when a concrete 
  **VconProcessor* is registered, it is loaded from a given package,
  given a unique name and instantiated from the given class name from
  that package.  The allow serveral instances of a concrete 
  **VconProcessor** to be instantiated, each with a unique name and
  different set of initialization options.  The class MUST also
  implement a static parameter: **initialization_options_class**.
  The **initialization_options_class** value MUST be the derived
  class of **VconProcessorInitializationOptions** that is used to
  validate the options provided to the concrete **VconProcessor**
  __init__ method.
  
 - **Initialization options Object:** [py_vcon_server.processor.VconProcessorInitOptions](#py_vcon_serverprocessorvconprocessorinitoptions)
 - **Processing options Object:** [py_vcon_server.processor.VconProcessorOptions](#py_vcon_serverprocessorvconprocessoroptions)


## py_vcon_server.processor.builtin.deepgram.Deepgram 

 - **Name:** deepgram 
 - **Version:** 0.0.1
 - **Summary:** transcribe Vcon dialogs using Vcon Whisper filter_plugin

Deepgram transcription binding for **VconProcessor**

This **VconProcessor** will transcribe one or all of the audio dialogs in the input Vcon and add analysis object(s) containing the transcription for the dialogs.
The **Deepgram** **Vcon** **filter_plug** for transcription is used.
      
 - **Initialization options Object:** [py_vcon_server.processor.builtin.deepgram.DeepgramInitOptions](#py_vcon_serverprocessorbuiltindeepgramdeepgraminitoptions)
 - **Processing options Object:** [py_vcon_server.processor.builtin.deepgram.DeepgramOptions](#py_vcon_serverprocessorbuiltindeepgramdeepgramoptions)


## py_vcon_server.processor.builtin.openai.OpenAiChatCompletion 

 - **Name:** openai_chat_completion 
 - **Version:** 0.0.1
 - **Summary:** transcribe Vcon dialogs using Vcon Whisper filter_plugin

OpenAi Chat Completion binding for **VconProcessor**

This **VconProcessor** will input the text dialog and transcribed dialog(s) for one or all of the audio dialogs in the input Vcon and add an analysis object containing the generative AI output for the prompt provided in the option.
The **openai_chat_completions** **Vcon** **filter_plug** is used.
      
 - **Initialization options Object:** [py_vcon_server.processor.builtin.openai.OpenAiChatCompletionInitOptions](#py_vcon_serverprocessorbuiltinopenaiopenaichatcompletioninitoptions)
 - **Processing options Object:** [py_vcon_server.processor.builtin.openai.OpenAiChatCompletionOptions](#py_vcon_serverprocessorbuiltinopenaiopenaichatcompletionoptions)


## py_vcon_server.processor.builtin.whisper.Whisper 

 - **Name:** whisper_base 
 - **Version:** 0.0.1
 - **Summary:** transcribe Vcon dialogs using Vcon Whisper filter_plugin

Whisper OpenAI transcription binding for **VconProcessor**  with model size: base

This **VconProcessor** will transcribe one or all of the audio dialogs in the input Vcon and add analysis object(s) containing the transcription for the dialogs.
The **Whisper** **Vcon** **filter_plug** for transcription is used which is built upon the OpenAI Whisper package.
      
 - **Initialization options Object:** [py_vcon_server.processor.builtin.whisper.WhisperInitOptions](#py_vcon_serverprocessorbuiltinwhisperwhisperinitoptions)
 - **Processing options Object:** [py_vcon_server.processor.builtin.whisper.WhisperOptions](#py_vcon_serverprocessorbuiltinwhisperwhisperoptions)




# Processor Initialization Options Classes

Init type: VconProcessorInitOptions
Init type: DeepgramInitOptions
Init type: OpenAiChatCompletionInitOptions
Init type: WhisperInitOptions


# Processor Options Classes

proc opt type: VconProcessorOptions
proc opt type: DeepgramOptions
proc opt type: OpenAiChatCompletionOptions
proc opt type: WhisperOptions

