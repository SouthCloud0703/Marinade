/**
 * This code was AUTOGENERATED using the codama library.
 * Please DO NOT EDIT THIS FILE, instead use visitors
 * to add features, then rerun codama to update it.
 *
 * @see https://github.com/codama-idl/codama
 */

import {
  combineCodec,
  fixDecoderSize,
  fixEncoderSize,
  getBytesDecoder,
  getBytesEncoder,
  getStructDecoder,
  getStructEncoder,
  transformEncoder,
  type Address,
  type Codec,
  type Decoder,
  type Encoder,
  type IAccountMeta,
  type IAccountSignerMeta,
  type IInstruction,
  type IInstructionWithAccounts,
  type IInstructionWithData,
  type ReadonlyAccount,
  type ReadonlySignerAccount,
  type ReadonlyUint8Array,
  type TransactionSigner,
  type WritableAccount,
} from '@solana/kit'
import { VALIDATOR_BONDS_PROGRAM_ADDRESS } from '../programs'
import { getAccountMetaFactory, type ResolvedAccount } from '../shared'

export const FUND_BOND_DISCRIMINATOR = new Uint8Array([
  58, 44, 212, 175, 30, 17, 68, 62,
])

export function getFundBondDiscriminatorBytes() {
  return fixEncoderSize(getBytesEncoder(), 8).encode(FUND_BOND_DISCRIMINATOR)
}

export type FundBondInstruction<
  TProgram extends string = typeof VALIDATOR_BONDS_PROGRAM_ADDRESS,
  TAccountConfig extends string | IAccountMeta<string> = string,
  TAccountBond extends string | IAccountMeta<string> = string,
  TAccountBondsWithdrawerAuthority extends
    | string
    | IAccountMeta<string> = string,
  TAccountStakeAccount extends string | IAccountMeta<string> = string,
  TAccountStakeAuthority extends string | IAccountMeta<string> = string,
  TAccountClock extends string | IAccountMeta<string> = string,
  TAccountStakeHistory extends string | IAccountMeta<string> = string,
  TAccountStakeProgram extends string | IAccountMeta<string> = string,
  TAccountEventAuthority extends string | IAccountMeta<string> = string,
  TAccountProgram extends string | IAccountMeta<string> = string,
  TRemainingAccounts extends readonly IAccountMeta<string>[] = [],
> = IInstruction<TProgram> &
  IInstructionWithData<Uint8Array> &
  IInstructionWithAccounts<
    [
      TAccountConfig extends string
        ? ReadonlyAccount<TAccountConfig>
        : TAccountConfig,
      TAccountBond extends string
        ? ReadonlyAccount<TAccountBond>
        : TAccountBond,
      TAccountBondsWithdrawerAuthority extends string
        ? ReadonlyAccount<TAccountBondsWithdrawerAuthority>
        : TAccountBondsWithdrawerAuthority,
      TAccountStakeAccount extends string
        ? WritableAccount<TAccountStakeAccount>
        : TAccountStakeAccount,
      TAccountStakeAuthority extends string
        ? ReadonlySignerAccount<TAccountStakeAuthority> &
            IAccountSignerMeta<TAccountStakeAuthority>
        : TAccountStakeAuthority,
      TAccountClock extends string
        ? ReadonlyAccount<TAccountClock>
        : TAccountClock,
      TAccountStakeHistory extends string
        ? ReadonlyAccount<TAccountStakeHistory>
        : TAccountStakeHistory,
      TAccountStakeProgram extends string
        ? ReadonlyAccount<TAccountStakeProgram>
        : TAccountStakeProgram,
      TAccountEventAuthority extends string
        ? ReadonlyAccount<TAccountEventAuthority>
        : TAccountEventAuthority,
      TAccountProgram extends string
        ? ReadonlyAccount<TAccountProgram>
        : TAccountProgram,
      ...TRemainingAccounts,
    ]
  >

export type FundBondInstructionData = { discriminator: ReadonlyUint8Array }

export type FundBondInstructionDataArgs = {}

export function getFundBondInstructionDataEncoder(): Encoder<FundBondInstructionDataArgs> {
  return transformEncoder(
    getStructEncoder([['discriminator', fixEncoderSize(getBytesEncoder(), 8)]]),
    value => ({ ...value, discriminator: FUND_BOND_DISCRIMINATOR }),
  )
}

export function getFundBondInstructionDataDecoder(): Decoder<FundBondInstructionData> {
  return getStructDecoder([
    ['discriminator', fixDecoderSize(getBytesDecoder(), 8)],
  ])
}

export function getFundBondInstructionDataCodec(): Codec<
  FundBondInstructionDataArgs,
  FundBondInstructionData
> {
  return combineCodec(
    getFundBondInstructionDataEncoder(),
    getFundBondInstructionDataDecoder(),
  )
}

export type FundBondInput<
  TAccountConfig extends string = string,
  TAccountBond extends string = string,
  TAccountBondsWithdrawerAuthority extends string = string,
  TAccountStakeAccount extends string = string,
  TAccountStakeAuthority extends string = string,
  TAccountClock extends string = string,
  TAccountStakeHistory extends string = string,
  TAccountStakeProgram extends string = string,
  TAccountEventAuthority extends string = string,
  TAccountProgram extends string = string,
> = {
  config: Address<TAccountConfig>
  /** bond account to be deposited to with the provided stake account */
  bond: Address<TAccountBond>
  /** new owner of the stake_account, it's the bonds withdrawer authority */
  bondsWithdrawerAuthority: Address<TAccountBondsWithdrawerAuthority>
  /** stake account to be deposited */
  stakeAccount: Address<TAccountStakeAccount>
  /** authority signature permitting to change the stake_account authorities */
  stakeAuthority: TransactionSigner<TAccountStakeAuthority>
  clock: Address<TAccountClock>
  stakeHistory: Address<TAccountStakeHistory>
  stakeProgram: Address<TAccountStakeProgram>
  eventAuthority: Address<TAccountEventAuthority>
  program: Address<TAccountProgram>
}

export function getFundBondInstruction<
  TAccountConfig extends string,
  TAccountBond extends string,
  TAccountBondsWithdrawerAuthority extends string,
  TAccountStakeAccount extends string,
  TAccountStakeAuthority extends string,
  TAccountClock extends string,
  TAccountStakeHistory extends string,
  TAccountStakeProgram extends string,
  TAccountEventAuthority extends string,
  TAccountProgram extends string,
  TProgramAddress extends Address = typeof VALIDATOR_BONDS_PROGRAM_ADDRESS,
>(
  input: FundBondInput<
    TAccountConfig,
    TAccountBond,
    TAccountBondsWithdrawerAuthority,
    TAccountStakeAccount,
    TAccountStakeAuthority,
    TAccountClock,
    TAccountStakeHistory,
    TAccountStakeProgram,
    TAccountEventAuthority,
    TAccountProgram
  >,
  config?: { programAddress?: TProgramAddress },
): FundBondInstruction<
  TProgramAddress,
  TAccountConfig,
  TAccountBond,
  TAccountBondsWithdrawerAuthority,
  TAccountStakeAccount,
  TAccountStakeAuthority,
  TAccountClock,
  TAccountStakeHistory,
  TAccountStakeProgram,
  TAccountEventAuthority,
  TAccountProgram
> {
  // Program address.
  const programAddress =
    config?.programAddress ?? VALIDATOR_BONDS_PROGRAM_ADDRESS

  // Original accounts.
  const originalAccounts = {
    config: { value: input.config ?? null, isWritable: false },
    bond: { value: input.bond ?? null, isWritable: false },
    bondsWithdrawerAuthority: {
      value: input.bondsWithdrawerAuthority ?? null,
      isWritable: false,
    },
    stakeAccount: { value: input.stakeAccount ?? null, isWritable: true },
    stakeAuthority: { value: input.stakeAuthority ?? null, isWritable: false },
    clock: { value: input.clock ?? null, isWritable: false },
    stakeHistory: { value: input.stakeHistory ?? null, isWritable: false },
    stakeProgram: { value: input.stakeProgram ?? null, isWritable: false },
    eventAuthority: { value: input.eventAuthority ?? null, isWritable: false },
    program: { value: input.program ?? null, isWritable: false },
  }
  const accounts = originalAccounts as Record<
    keyof typeof originalAccounts,
    ResolvedAccount
  >

  const getAccountMeta = getAccountMetaFactory(programAddress, 'programId')
  const instruction = {
    accounts: [
      getAccountMeta(accounts.config),
      getAccountMeta(accounts.bond),
      getAccountMeta(accounts.bondsWithdrawerAuthority),
      getAccountMeta(accounts.stakeAccount),
      getAccountMeta(accounts.stakeAuthority),
      getAccountMeta(accounts.clock),
      getAccountMeta(accounts.stakeHistory),
      getAccountMeta(accounts.stakeProgram),
      getAccountMeta(accounts.eventAuthority),
      getAccountMeta(accounts.program),
    ],
    programAddress,
    data: getFundBondInstructionDataEncoder().encode({}),
  } as FundBondInstruction<
    TProgramAddress,
    TAccountConfig,
    TAccountBond,
    TAccountBondsWithdrawerAuthority,
    TAccountStakeAccount,
    TAccountStakeAuthority,
    TAccountClock,
    TAccountStakeHistory,
    TAccountStakeProgram,
    TAccountEventAuthority,
    TAccountProgram
  >

  return instruction
}

export type ParsedFundBondInstruction<
  TProgram extends string = typeof VALIDATOR_BONDS_PROGRAM_ADDRESS,
  TAccountMetas extends readonly IAccountMeta[] = readonly IAccountMeta[],
> = {
  programAddress: Address<TProgram>
  accounts: {
    config: TAccountMetas[0]
    /** bond account to be deposited to with the provided stake account */
    bond: TAccountMetas[1]
    /** new owner of the stake_account, it's the bonds withdrawer authority */
    bondsWithdrawerAuthority: TAccountMetas[2]
    /** stake account to be deposited */
    stakeAccount: TAccountMetas[3]
    /** authority signature permitting to change the stake_account authorities */
    stakeAuthority: TAccountMetas[4]
    clock: TAccountMetas[5]
    stakeHistory: TAccountMetas[6]
    stakeProgram: TAccountMetas[7]
    eventAuthority: TAccountMetas[8]
    program: TAccountMetas[9]
  }
  data: FundBondInstructionData
}

export function parseFundBondInstruction<
  TProgram extends string,
  TAccountMetas extends readonly IAccountMeta[],
>(
  instruction: IInstruction<TProgram> &
    IInstructionWithAccounts<TAccountMetas> &
    IInstructionWithData<Uint8Array>,
): ParsedFundBondInstruction<TProgram, TAccountMetas> {
  if (instruction.accounts.length < 10) {
    // TODO: Coded error.
    throw new Error('Not enough accounts')
  }
  let accountIndex = 0
  const getNextAccount = () => {
    const accountMeta = instruction.accounts![accountIndex]!
    accountIndex += 1
    return accountMeta
  }
  return {
    programAddress: instruction.programAddress,
    accounts: {
      config: getNextAccount(),
      bond: getNextAccount(),
      bondsWithdrawerAuthority: getNextAccount(),
      stakeAccount: getNextAccount(),
      stakeAuthority: getNextAccount(),
      clock: getNextAccount(),
      stakeHistory: getNextAccount(),
      stakeProgram: getNextAccount(),
      eventAuthority: getNextAccount(),
      program: getNextAccount(),
    },
    data: getFundBondInstructionDataDecoder().decode(instruction.data),
  }
}
