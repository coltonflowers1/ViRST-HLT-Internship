# Hybrid Code Networks

Hybrid code networks (HCNs) are dialog systems that use handwritten rules and are trained using an RNN. The implementation is written in Python. The RNN (LSTM) is built with TensorFlow. This particular version implements Dialog-State-Tracking(DST) as an automaton.


Current Version:
The file 'data/tagged_virst_train_new_summary.txt' is used for training.

__USAGE NOTES__ 
 * using `BERT`: open a separate terminal and start the bert server before staring the dialogue system:  
   ```bash
   bert-serving-start -model_dir uncased_L-12_H-768_A-12/ -tuned_model_dir uncased_L-12_H-768_A-12/ -ckpt_name model.ckpt-41 -num_worker 4
   ```
 * for `interaction mode`, 2 terminals/consoles are needed, one for running the HCN as a service and one for input/ouput interaction:  
   ````bash
   ## MacOS / *nix
   python3 virstInteractionConsole.py
   ## Windows
   python virstInteractionConsole.py
   ````
 * to use a different pre-trained model, add the .ckpt file to the model_dir and change the -ckpt_name argument to the pre-trained model of interest.
 
 * to train ones own bert model on a classification task, the training data, dev data, and testing data must all be in a format identical to that laid out in the tsv files inside bert_intent_data.
    -BERT must be installd using
        pip install bert
    -Then go into the BERT repository and then inside the repository, enable multiclass classification by going into bert/run_classifier and replacing the body of the get_labels method of the ColaProcessor class to 
        [str(x) for x in range(15)] with 15 replaced with your number of classes. 
    -Train and dev data is a tsv containing 4 columns, 
    the first column is irrelevant and can be filled with just 1's, the second is the index of the classification, the third is another throw away column, and 
    the last is the sentence to be classified. There is no header.
    -Test data is split into two columns, the first is the classification index, and the second is the sentence. This tsv must have a header with 'id' in the first column and 'utt' in the second. 
    -Run the shell script called 'bert_script' after changing the base directory within the script to be the directory containing the base bert model, ie uncased_L-12_H-768_A-12
    
    
 
 
## Operational Loop

![](https://raw.githubusercontent.com/voicy-ai/DialogStateTracking/master/images/hcn-block-diagram.png)


## Setup

### prerequisites

 * Python 3.x amd64
 * git (OPTIONAL)

### install prerequisites
```bash
git checkout tidyInteractive

## MacOS / *nix
sudo -H pip3 install -r requirements.txt
python3 -m spacy download de
python3 -m spacy download en_core_web_sm

## Windows
python -m pip install -r requirements.txt
python -m spacy download de
python -m spacy download en_core_web_sm
```

Open your terminal and run
```bash
python
```
then run:
```python
import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger');
```

For the embeddings it is necessary to have a _GloVe_ or _w2v_ model compatible with gensim  at `/data`, e.g.  
download ZIP file from [cloud.dfki.de/owncloud/glove_de_model.zip](https://cloud.dfki.de/owncloud/index.php/s/DyaxYxrb77aDtRt)
an extract `glove_de_model.bin` from the ZIP to `/data/glove_de_model.bin`.

For English _GloVe_ embeddings download `glove_en_model.zip` from
[cloud.dfki.de/owncloud/glove_en_model.zip](https://cloud.dfki.de/owncloud/index.php/s/GewYSz3TGw3e2LL)
and extract the file `glove_en_model.bin` into directory `/data`.

For `BERT` encodings download
[cloud.dfki.de/owncloud/bert_model.ckpt.data-00000-of-00001.zip](https://cloud.dfki.de/owncloud/index.php/s/tmJktryQweceMEj)
and
[cloud.dfki.de/owncloud/model.ckpt-41.data-00000-of-00001.zip](https://cloud.dfki.de/owncloud/index.php/s/dkxbSB89Aoxj6xn)
and extract the files into directory `/uncased_L-12_H-768_A-12`.



## Note on AIML

Since Version 2, the HCN is connected with AIML (Artificial Intelligence Markup Language). AIML is a standard XML format for defining a chatbot's responses.
After installing the prerequisites, you might want to comment some lines in the file Kernel.py from the aiml package. The path where you find it could look like the following:

/path/to/miniconda3/envs/env_name/lib/python3.5/site-packages/aiml/Kernel.py  
(if you have installed it in an environment)

Comment the lines 328, 343 and 344, so that no unnecessary lines are printed to the console while interacting with the chatbot.

<img src="images/aiml-kernel.png"  width="545" height="388">


## Execution

```bash
# training
python3 virstBot.py train
# default values for ratio, epochs and ngram_size are provided in Bot.py,
#  but you can change them upon execution, for example:
python3 virstBot.py train train_ratio=3/5 epochs=50
# trained model is saved to ckpt/

# interaction
python3 virstBot.py interact
# checkpoint from ckpt/ is loaded
# open additional terminal and run
python3 virstInteractionConsole.py
# start interaction

# verbose interaction
python3 virstBot.py interact verbose
# checkpoint from ckpt/ is loaded
# open additional terminal and run
python3 virstInteractionConsole.py
# start interaction
# predicted utterance type, current state and dialogacts are printed

# verbose interaction
python3 virstBot.py interact update
# checkpoint from ckpt/ is loaded
# open additional terminal and run
python3 virstInteractionConsole.py
# start interaction
# updates checkpoint after session
```


## Sample Interaction from Version 1

<img src="images/sample-interaction.png"  width="633" height="470">


## Acknowledgements

The original implementation of hybrid code networks can be found at <https://github.com/voicy-ai/DialogStateTracking/tree/master/src/hcn>.  
The Python 3 interpreter for AIML was retrieved from <https://github.com/paulovn/python-aiml>.  
The German word embeddings were taken from <https://devmount.github.io/GermanWordEmbeddings/>.  
Thanks a lot to Mino for his extensions to the germanHCN! He has added a couple of files to the data and modules subdirectories and modified the execution of the training and interaction scripts.
