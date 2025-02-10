#!/usr/bin/env python3
import sys
import csv
csv.field_size_limit(sys.maxsize)  # Increase CSV field size limit

import os
import json
import glob
import re
import logging
from web3 import Web3

# --------------------------- CONFIGURATION ---------------------------
RPC_URL = "https://rpc.genesisl1.org"
CONTRACT_ADDRESS = "ADDRESS_OF_MOLNFT_SMART_CONTRACT"
CHAIN_ID = 29
GAS_PRICE = Web3.to_wei("51", "gwei")

FIRST_OWNER = "ENTER_FIRST_NFT_OWNER_HERE"
PRIVATE_KEY = "PRIVATE_KEY_OF_DEPLOYER_OR_EDITOR"  # Insert your private key here, NEVER SHARE YOUR PRIVATE KEY! DEPLOY IN SAFE ENVIRONMENT!

METADATA_CSV = "example/metadata.csv"
IMAGES_DIR   = "example/images_230_base64"
MOLECULAR_DIR= "example/final_bcif_output"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# --------------------------- CONTRACT ABI ---------------------------
CONTRACT_ABI = json.loads(r'''
[
	{
		"inputs": [],
		"name": "ERC721EnumerableForbiddenBatchMint",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "ERC721IncorrectOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ERC721InsufficientApproval",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "approver",
				"type": "address"
			}
		],
		"name": "ERC721InvalidApprover",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			}
		],
		"name": "ERC721InvalidOperator",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "ERC721InvalidOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "receiver",
				"type": "address"
			}
		],
		"name": "ERC721InvalidReceiver",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			}
		],
		"name": "ERC721InvalidSender",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ERC721NonexistentToken",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "index",
				"type": "uint256"
			}
		],
		"name": "ERC721OutOfBoundsIndex",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "OwnableInvalidOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "OwnableUnauthorizedAccount",
		"type": "error"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "approved",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "Approval",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "ApprovalForAll",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "parentId",
				"type": "uint256"
			}
		],
		"name": "ChildNFTMinted",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "EditorAdded",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "EditorRemoved",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ParentNFTMinted",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "Transfer",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "addEditor",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "approve",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"name": "batchTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "IDCODE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "HEADER",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "ACCESSION_DATE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "COMPOUND",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "SOURCE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "AUTHOR_LIST",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "RESOLUTION",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "EXPERIMENT_TYPE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "SEQUENCE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "imageBase64",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "fileBase64",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "parentId",
				"type": "uint256"
			}
		],
		"name": "mintNFT",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "removeEditor",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "renounceOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "safeTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "bytes",
				"name": "data",
				"type": "bytes"
			}
		],
		"name": "safeTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "setApprovalForAll",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bool",
				"name": "status",
				"type": "bool"
			}
		],
		"name": "setOnlyDeployerCanMint",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "transferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "IDCODE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "HEADER",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "ACCESSION_DATE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "COMPOUND",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "SOURCE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "AUTHOR_LIST",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "RESOLUTION",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "EXPERIMENT_TYPE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "SEQUENCE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "imageBase64",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "fileBase64",
				"type": "string"
			}
		],
		"name": "updateMetadata",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "balanceOf",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "getApproved",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "parentId",
				"type": "uint256"
			}
		],
		"name": "getChildren",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "childIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "parentId",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "getChildrenPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "childIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "parentId",
				"type": "uint256"
			}
		],
		"name": "getCombinedData",
		"outputs": [
			{
				"internalType": "string",
				"name": "combinedFileBase64",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "parentId",
				"type": "uint256"
			}
		],
		"name": "getEntireNFT",
		"outputs": [
			{
				"internalType": "string",
				"name": "IDCODE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "HEADER",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "ACCESSION_DATE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "COMPOUND",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "SOURCE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "AUTHOR_LIST",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "RESOLUTION",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "EXPERIMENT_TYPE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "SEQUENCE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "imageBase64",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "combinedFileBase64",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "getMetadata",
		"outputs": [
			{
				"internalType": "string",
				"name": "IDCODE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "HEADER",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "ACCESSION_DATE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "COMPOUND",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "SOURCE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "AUTHOR_LIST",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "RESOLUTION",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "EXPERIMENT_TYPE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "SEQUENCE",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "imageBase64",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "fileBase64",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "getParent",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			}
		],
		"name": "isApprovedForAll",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "name",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nextChildId",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nextNFTId",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "onlyDeployerCanMint",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ownerOf",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			}
		],
		"name": "searchByACCESSION_DATE",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "searchByACCESSION_DATEPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			}
		],
		"name": "searchByAUTHOR_LIST",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "searchByAUTHOR_LISTPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			}
		],
		"name": "searchByCOMPOUND",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "searchByCOMPOUNDPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			}
		],
		"name": "searchByEXPERIMENT_TYPE",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "searchByEXPERIMENT_TYPEPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			}
		],
		"name": "searchByHEADER",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "searchByHEADERPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			}
		],
		"name": "searchByIDCODE",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "searchByIDCODEPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			}
		],
		"name": "searchByRESOLUTION",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "searchByRESOLUTIONPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			}
		],
		"name": "searchBySEQUENCE",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "searchBySEQUENCEPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			}
		],
		"name": "searchBySOURCE",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "searchTerm",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "offset",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "searchBySOURCEPaginated",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "tokenIds",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256",
				"name": "total",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes4",
				"name": "interfaceId",
				"type": "bytes4"
			}
		],
		"name": "supportsInterface",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "symbol",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "index",
				"type": "uint256"
			}
		],
		"name": "tokenByIndex",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "tokenExists",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "index",
				"type": "uint256"
			}
		],
		"name": "tokenOfOwnerByIndex",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "tokenURI",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "totalSupply",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
''')

def load_contract(web3):
    return web3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=CONTRACT_ABI
    )

def read_csv_data(csv_file):
    rows = []
    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized = {k.strip().upper(): v for k, v in row.items() if k is not None}
            rows.append(normalized)
    return rows

def read_file_contents(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None

def get_image_for_idcode(idcode):
    idcode_lower = idcode.lower()
    pattern = os.path.join(IMAGES_DIR, f"{idcode_lower}*.base64.txt")
    files = glob.glob(pattern)
    if not files:
        pattern = os.path.join(IMAGES_DIR, f"{idcode}*.base64.txt")
        files = glob.glob(pattern)
        if not files:
            logging.error(f"No image file found for IDCODE {idcode}")
            return None
    # Prefer a file without "_part"
    for file in files:
        if "_part" not in os.path.basename(file):
            return read_file_contents(file)
    return read_file_contents(files[0])

def get_molecular_files_for_idcode(idcode):
    idcode_lower = idcode.lower()
    pattern = os.path.join(MOLECULAR_DIR, f"{idcode_lower}*.bcif.gz.base64*")
    files = glob.glob(pattern)
    if not files:
        pattern = os.path.join(MOLECULAR_DIR, f"{idcode}*.bcif.gz.base64*")
        files = glob.glob(pattern)
        if not files:
            logging.error(f"No molecular data file found for IDCODE {idcode}")
            return None, []
    parent_file = None
    parts = []
    for file in files:
        base = os.path.basename(file)
        if "_part" in base:
            m = re.search(r"_part(\d+)", base)
            if m:
                parts.append((int(m.group(1)), file))
        else:
            parent_file = file
    parts.sort(key=lambda x: x[0])
    return parent_file, [f for _, f in parts]

def mint_transaction(web3, func, account, nonce):
    """
    Build, sign, and send a transaction in snake_case. 
    'estimate_gas' -> 'build_transaction' -> 'sign_transaction' -> 'raw_transaction'.
    """
    try:
        gas_estimate = func.estimate_gas({'from': account.address})
        gas_limit = gas_estimate + 10000
    except Exception as e:
        logging.warning(f"Gas estimate failed: {e}. Using 300000.")
        gas_limit = 300000

    tx = func.build_transaction({
        'chainId': CHAIN_ID,
        'gas': gas_limit,
        'gasPrice': GAS_PRICE,
        'nonce': nonce
    })

    # sign in snake_case
    signed_tx = account.sign_transaction(tx)

    # send the raw_transaction in snake_case
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    logging.info(f"Transaction sent: {tx_hash.hex()}")

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    logging.info(f"Transaction confirmed: {receipt.transactionHash.hex()}")
    return receipt

def main():
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not web3.is_connected():
        logging.error("Unable to connect to the Web3 provider.")
        return
    logging.info("Connected to Web3 provider.")

    contract = load_contract(web3)
    account  = web3.eth.account.from_key(PRIVATE_KEY)
    logging.info(f"Using account: {account.address}")

    nonce = web3.eth.get_transaction_count(account.address)

    # Read CSV
    try:
        rows = read_csv_data(METADATA_CSV)
    except Exception as e:
        logging.error(f"Error reading CSV: {e}")
        return
    logging.info(f"Found {len(rows)} rows in CSV.")

    for row in rows:
        idcode_raw = row.get("IDCODE")
        if not idcode_raw or not idcode_raw.strip():
            logging.error("Skipping row with missing/empty IDCODE.")
            continue

        idcode = idcode_raw.strip()
        logging.info(f"Processing NFT with IDCODE: {idcode}")

        image_data = get_image_for_idcode(idcode)
        if image_data is None:
            logging.error(f"Skipping NFT {idcode} - missing image file.")
            continue

        parent_file, part_files = get_molecular_files_for_idcode(idcode)
        if (parent_file is None) and not part_files:
            logging.error(f"Skipping NFT {idcode} - missing molecular data.")
            continue

        # Additional CSV fields
        HEADER          = row.get("HEADER", "").strip()
        ACCESSION_DATE  = row.get("ACCESSION_DATE", "").strip()
        COMPOUND        = row.get("COMPOUND", "").strip()
        SOURCE          = row.get("SOURCE", "").strip()
        AUTHOR_LIST     = row.get("AUTHOR_LIST", "").strip()
        RESOLUTION      = row.get("RESOLUTION", "").strip()
        EXPERIMENT_TYPE = row.get("EXPERIMENT_TYPE", "").strip()
        SEQUENCE        = row.get("SEQUENCE", "").strip()

        if part_files:
            logging.info(f"Minting hierarchical NFT for {idcode} with {len(part_files)} parts.")
            # 1) parent
            try:
                parent_func = contract.functions.mintNFT(
                    FIRST_OWNER,
                    idcode,
                    HEADER,
                    ACCESSION_DATE,
                    COMPOUND,
                    SOURCE,
                    AUTHOR_LIST,
                    RESOLUTION,
                    EXPERIMENT_TYPE,
                    SEQUENCE,
                    image_data,
                    "",
                    0
                )
                receipt = mint_transaction(web3, parent_func, account, nonce)
                nonce += 1
            except Exception as e:
                logging.error(f"Error minting parent NFT {idcode}: {e}")
                continue

            # 2) read event
            parent_token_id = None
            try:
                events = contract.events.ParentNFTMinted().process_receipt(receipt)
                if events and len(events) > 0:
                    parent_token_id = events[0]['args']['tokenId']
                    logging.info(f"Parent minted tokenId: {parent_token_id}")
                else:
                    logging.error("No ParentNFTMinted event found in receipt.")
                    continue
            except Exception as e:
                logging.error(f"Error reading event for parent NFT {idcode}: {e}")
                continue

            # 3) children
            sorted_parts = []
            for f in part_files:
                base = os.path.basename(f)
                m = re.search(r"_part(\d+)", base)
                if m:
                    sorted_parts.append((int(m.group(1)), f))
            sorted_parts.sort(key=lambda x: x[0])

            for part_number, part_file in sorted_parts:
                part_data = read_file_contents(part_file)
                if not part_data:
                    logging.error(f"Skipping child NFT {idcode} part {part_number}, read error.")
                    continue
                try:
                    child_func = contract.functions.mintNFT(
                        FIRST_OWNER,
                        "", "", "", "", "", "", "", "", "",
                        "",  # no image
                        part_data,
                        parent_token_id
                    )
                    receipt = mint_transaction(web3, child_func, account, nonce)
                    nonce += 1
                    logging.info(f"Child NFT for {idcode} part {part_number} minted OK.")
                except Exception as e:
                    logging.error(f"Error minting child NFT for {idcode} part {part_number}: {e}")
                    continue

        else:
            # standard
            logging.info(f"Minting standard NFT for {idcode}")
            file_data = read_file_contents(parent_file)
            if not file_data:
                logging.error(f"Skipping NFT {idcode}, read error on molecular file.")
                continue
            try:
                standard_func = contract.functions.mintNFT(
                    FIRST_OWNER,
                    idcode,
                    HEADER,
                    ACCESSION_DATE,
                    COMPOUND,
                    SOURCE,
                    AUTHOR_LIST,
                    RESOLUTION,
                    EXPERIMENT_TYPE,
                    SEQUENCE,
                    image_data,
                    file_data,
                    0
                )
                receipt = mint_transaction(web3, standard_func, account, nonce)
                nonce += 1
                logging.info(f"NFT {idcode} minted successfully.")
            except Exception as e:
                logging.error(f"Error minting NFT for {idcode}: {e}")
                continue

if __name__ == "__main__":
    main()
