import cohere

from cohere.responses.classify import Example


def train_emotions(emotion):
    emotion_examples = []
    file = open('training_data/' + emotion + ".txt", 'r')
    sentences = file.readlines()
    for sentence in sentences:
        emotion_examples.append(Example(sentence, emotion))
    return emotion_examples


def get_mood_examples():
  examples = []
  emotions = ["Angry", "Calm", "Fear", "Happy", "Insightful", "Sad", "Worry"]

  for emotion in emotions:
      examples.extend(train_emotions(emotion))

  return examples