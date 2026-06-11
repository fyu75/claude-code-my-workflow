## **MSRB HISTORICAL TRANSACTION DATA REPORT FORMAT** 

The following fields are included in the Historical Transaction Data Reports. For complete information please refer to the Specifications Document for the RTRS Subscription Service. 

## _**RTRS Control Number (variable name: RTRS_CONTROL_NUMBER)**_ 

The RTRS ID for the transaction. This may be used to apply subsequent modifications and cancellations to an initial transaction. Format: up to 16 characters. 

RTRS Control Number is unique for a trade for 10-year period. 

## _**Trade Type Indicator (variable name: TRADE_TYPE_INDICATOR)**_ 

Type of trade: an inter-dealer trade (D), a purchase from a customer by a dealer (P) or a sale to a customer by a dealer (S). Format: one character. 

## _**CUSIP (variable name: CUSIP)**_ 

The CUSIP number of the issue traded. Format: nine characters including the checksum digit. 

CUSIP is fixed for a security.  For a certain CUSIP, the values in “Security Description”, “dated_date”, “maturity_date”, should be the same, but because they may come from different sources, different values may have been entered.  Some discrepancies may exist but they shouldn’t be significantly different. 

## _**Security Description (variable name: SECURITY_DESCRIPTION)**_ 

Text description of the security. Format: up to 120 characters of free format text. 

## _**Dated Date (variable name: DATED_DATE)**_ 

Dated date of the issue traded. Format: YYYYMMDD. 

## - According to http://www.msrb.org/Glossary/Definition/DATED DATE.aspx: 

DATED DATE is the date from which interest on a new issue of municipal securities typically starts to accrue. This date is often used to identify a particular series of bonds of an issuer. 

## _**Coupon (if available) (variable name: COUPON)**_ 

Interest rate of the issue traded. Will be blank for zero-coupon bonds. Format: fixed decimal, up to six digits, nnn.nnn. 

## _**Maturity Date  (variable name: MATURITY_DATE)**_ 

Maturity date of the issue traded. Format: YYYYMMDD. 

## _**When-Issued Indicator (if applicable) (variable name: WHEN_ISSUED_INDICATOR)**_ 

An indicator (Y) of whether the issue traded on or before the issue’s initial settlement date. Format: one character. 

## _**Assumed Settlement Date  (variable name: ASSUMED_SETTLEMENT_DATE)**_ 

For new issues where the initial settlement date is not known at the time of execution, this field is a date 15 business days after trade date. If both Settlement Date and Assumed Settlement Date are populated, use Settlement Date. Format: YYYYMMDD. 

## _**Trade Date  (variable name: TRADE_DATE)**_ 

The date the trade was executed. Format: YYYYMMDD. 

## _**Time of Trade  (variable name: TIME_OF_TRADE)**_ 

The time of trade execution reported by the dealer. Format: HHMMSS (24-hour system) 

## _**Settlement Date (if known) (variable name: SETTLEMENT_DATE)**_ 

The settlement date of the trade if known. If both Settlement Date and Assumed Settlement Date are populated, use Settlement Date. Format: YYYYMMDD. 

_**Par Traded (variable name: PAR_TRADED)**_ 

The par value of the trade. Trades with a par amount over $5 million will show par value as “MM+” until five days after their trade date. Format: fixed decimal, up to 12 digits, nnnnnnnnnn.nn 

## _**Dollar Price  (variable name: DOLLAR_PRICE)**_ 

The dollar price of the trade. Format: fixed decimal, up to seven digits, nnnn.nnn 

## _**Yield (if applicable) (variable name: YIELD)**_ 

The yield of the trade. Format: fixed decimal, up to six digits, may be negative, [-]nnn.nnn 

Yield is based on a "yield to worst," that may be realized on an investment in the security based on the settlement date, price, interest rate on the security and the remaining period until maturity or earlier redemption. 

This value is calculated by the MSRB.  There are times when this field is not provided/calculated, particularly for variable rate securities.  If it’s not provided, it can’t be calculated. 

## _**Broker’s Broker Indicator (if applicable) (variable name: BROKERS_BROKER_INDICATOR)**_ 

An indicator used in inter-dealer transactions that were executed by a broker’s broker, including whether it was a purchase (P) or sale (S) by the broker’s broker. Format: one character. 

## _**Weighted Price Indicator (if applicable) (variable name: WEIGHTED_PRICE_INDICATOR)**_ 

An indicator (Y) that the transaction price was a “weighted average price” based on multiple transactions done at different prices earlier in the day to accumulate the par amount needed to make this transaction. Format: one character. 

## _**List Offering Price/Takedown Indicator (if applicable) (variable name: OFFER_PRICE_TAKEDOWN_INDICATOR)**_ 

An indicator (Y) showing that the transaction price was reported as a primary market sale transaction executed on the first day of trading of a new issue: 

-by a sole underwriter, syndicate manager, syndicate member or selling group member at the published list offering price for the security (“List Offering Price” ); or 

-by a sole underwriter, syndicate manager, syndicate member or selling group member at a discount from the published list offering price for the security (“RTRS Takedown Transaction”). 

Format: one character. 

## _**RTRS Publish Date  (variable name: RTRS_PUBLISH_DATE)**_ 

The date the data was produced for the report. Format: YYYYMMDD. 

## _**RTRS Publish Time  (variable name: RTRS_PUBLISH_TIME)**_ 

The time the data was produced for the report. Format: HHMMSS (24-hour system). 

## _**Version Number  (variable name: VERSION_NUMBER)**_ 

Version number of the message or file format used in the message or file. Format: up to four digits, fixed decimal, nn.nn. 

## _**Unable to Verify Dollar Price Indicator (if applicable) (variable name: UV_DOLLAR_PRICE_INDICATOR)**_ 

An indicator that the dollar price calculated by the MSRB does not match the dollar price submitted by the dealer, but falls within a one dollar tolerance for dissemination. 

_**Alternative Trading System (ATS) Indicator** (Field not present in files prior to July 18, 2016)_ _**(variable name: ATS_ INDICATOR)**_ 

An indicator (Y) showing that an inter-dealer transaction was executed with or using the services of an alternative trading system (ATS) with Form ATS on file with the SEC. 

_**Non-Transaction Based Compensation Arrangement (NTBC) Indicator** (Field not present in files prior to July 18, 2016)_ _**(variable name: NTBC_ INDICATOR)**_ 

An indicator (Y) showing that a customer transaction did not include a mark-up, mark-down or commission. 

## _**RTRS Control Number, CUSIP, and Trade Date combined together can uniquely identify a trade.**_ 

The above documentation file was copied and modified from https://www.msrb.org/markettransparency/subscription-services-and-products/msrb-transaction-subscription/historical-data-format The texts highlighted in red were added by WRDS and confirmed by MSRB. 

WRDS last updated this documentation file on 02/08/2022 

