from cs145lib.task0 import Channel, node_main

# Encoding
# Map each word to their index on the corpus
# Use 1st bit to say to receiver to start receiving
# Send word index as binary string
# Send 2^16 - 1 to indicate end receiving (if not 5 words)

def sender(channel: Channel, sentence: str) -> None:
    # Send signal to start reading
    channel.send(1)

    words = sentence.lower().split(' ')
    words[-1] = words[-1][:-1] # Remove period
    with open('corpus.txt', 'r') as file:
        corpus = file.read().splitlines()
    
        for word in words:
            index = corpus.index(word)
            # Pad binary string to 16
            bin_str = bin(index)[2:].zfill(16)
            for bit in map(int, bin_str):
                channel.send(bit)

    # Send EOS if not 5 words
    if len(words) != 5:
        for _ in range(16):
            channel.send(1)
    

def receiver(channel: Channel) -> str:
    # Ignore all zeroes until 1
    bit = 0
    while bit == 0:
        bit = channel.get()

    # Load corpus
    corpus = []
    with open('corpus.txt', 'r') as file:
        corpus = file.read().splitlines()

    # Iterate for max of 5 words
    sentence = ''
    for i in range(5):
        # Take 16 bits and convert to int
        bin_str = ''.join(str(channel.get()) for _ in range(16))
        index = int(bin_str, 2)

        # EOS
        if index == 2**16 - 1:
            break

        if i == 0:
            sentence += corpus[index].capitalize()
        else:
            sentence += corpus[index]
        
        sentence += ' '
        
    # Change last space to period
    return sentence[:-1] + '.'


if __name__ == '__main__':
    node_main(sender=sender, receiver=receiver)
