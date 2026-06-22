from blockchain.blockchain import get_blockchain

chain = get_blockchain()

valid, issues = chain.validate()

print("Length:", chain.length())
print("Valid:", valid)
print("Issues:", issues[:5])